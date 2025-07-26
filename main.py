from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from decimal import Decimal
import httpx
import os
from typing import Optional, List
from datetime import datetime, timedelta
import asyncio
from items import ITEMS, get_item_fetcher, get_items_by_category

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class ConvertResponse(BaseModel):
    quantity: float
    usd_item: float
    usd_total: float
    btc_price: float

class HistoricalResponse(BaseModel):
    dates: List[str]
    btc_prices: List[float]

# Cache for BTC price (5 min cache)
btc_price_cache = {"price": None, "timestamp": None}

async def get_btc_price() -> float:
    """Fetch current BTC price with caching"""
    now = datetime.now()
    
    # Check cache (5 minute expiry)
    if (btc_price_cache["price"] is not None and 
        btc_price_cache["timestamp"] is not None and
        (now - btc_price_cache["timestamp"]).seconds < 300):
        return btc_price_cache["price"]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            price = float(data["bitcoin"]["usd"])
            
            # Update cache
            btc_price_cache["price"] = price
            btc_price_cache["timestamp"] = now
            
            return price
    except Exception as e:
        # Fallback to cached value if available
        if btc_price_cache["price"] is not None:
            return btc_price_cache["price"]
        raise HTTPException(status_code=503, detail=f"Unable to fetch BTC price: {str(e)}")

@app.get("/")
async def serve_index():
    """Serve the main HTML page"""
    try:
        return FileResponse("index.html", media_type="text/html")
    except Exception:
        return FileResponse("static/index.html", media_type="text/html")

@app.get("/style.css")
async def serve_css():
    """Serve CSS file"""
    try:
        return FileResponse("style.css", media_type="text/css")
    except Exception:
        return FileResponse("static/style.css", media_type="text/css")

@app.get("/script.js")
async def serve_js():
    """Serve JavaScript file"""
    try:
        return FileResponse("script.js", media_type="application/javascript")
    except Exception:
        return FileResponse("static/script.js", media_type="application/javascript")

@app.get("/debug")
async def serve_debug():
    """Serve the debug HTML page"""
    return FileResponse("debug.html")

@app.get("/api/items")
async def get_items():
    """Get available items grouped by category"""
    return get_items_by_category()

@app.get("/api/convert", response_model=ConvertResponse)
async def convert(
    btc_amount: Optional[float] = Query(None),
    sats: bool = Query(False),
    item: str = Query(...),
    direction: str = Query("btc_to_item"),
    quantity: Optional[float] = Query(None)
):
    """Convert between BTC and item quantities"""
    
    # Validate direction
    if direction not in ["btc_to_item", "item_to_btc"]:
        raise HTTPException(status_code=400, detail="Direction must be 'btc_to_item' or 'item_to_btc'")
    
    # Validate item exists
    if item not in ITEMS:
        raise HTTPException(status_code=400, detail=f"Item '{item}' not found")
    
    try:
        # Get BTC price and item price concurrently
        btc_price_task = get_btc_price()
        item_fetcher = get_item_fetcher(item)
        item_price_task = item_fetcher()
        
        btc_price, item_price = await asyncio.gather(btc_price_task, item_price_task)
        
        if direction == "btc_to_item":
            # Validate BTC amount
            if btc_amount is None:
                raise HTTPException(status_code=400, detail="btc_amount is required for btc_to_item conversion")
            
            if btc_amount <= 0:
                raise HTTPException(status_code=400, detail="BTC amount must be positive")
            
            # Convert sats to BTC if needed
            btc_value = Decimal(str(btc_amount))
            if sats:
                btc_value = btc_value / Decimal("100000000")  # Convert sats to BTC
            
            # Calculate quantities
            usd_total = float(btc_value * Decimal(str(btc_price)))
            item_quantity = usd_total / item_price
            
            return ConvertResponse(
                quantity=round(item_quantity, 6),
                usd_item=round(item_price, 2),
                usd_total=round(usd_total, 2),
                btc_price=round(btc_price, 2)
            )
        
        else:  # item_to_btc
            # Validate quantity
            if quantity is None:
                raise HTTPException(status_code=400, detail="quantity is required for item_to_btc conversion")
            
            if quantity <= 0:
                raise HTTPException(status_code=400, detail="Quantity must be positive")
            
            # Calculate BTC needed
            usd_total = quantity * item_price
            btc_needed = usd_total / btc_price
            
            # Convert to sats if requested
            if sats:
                btc_needed = btc_needed * 100000000  # Convert BTC to sats
            
            return ConvertResponse(
                quantity=round(btc_needed, 8 if not sats else 0),
                usd_item=round(item_price, 2),
                usd_total=round(usd_total, 2),
                btc_price=round(btc_price, 2)
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")

@app.get("/api/historical", response_model=HistoricalResponse)
async def historical(
    item: str = Query(...),
    from_date: str = Query(...),
    to_date: str = Query(...)
):
    """Get historical price data for CPI items"""
    
    # Validate item exists and has historical support
    if item not in ITEMS:
        raise HTTPException(status_code=400, detail=f"Item '{item}' not found")
    
    item_info = ITEMS[item]
    if not item_info.get("historical_support", False):
        raise HTTPException(status_code=400, detail=f"Historical data not available for '{item}'")
    
    try:
        # Validate date format
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
        
        if from_dt >= to_dt:
            raise HTTPException(status_code=400, detail="from_date must be before to_date")
        
        # Limit to reasonable date range (max 2 years)
        if (to_dt - from_dt).days > 730:
            raise HTTPException(status_code=400, detail="Date range cannot exceed 2 years")
        
        # Get FRED series ID for the item
        fred_series = item_info.get("fred_series")
        if not fred_series:
            raise HTTPException(status_code=400, detail=f"No FRED series configured for '{item}'")
        
        # Fetch historical data from FRED API
        fred_api_key = os.getenv("FRED_API_KEY")
        if not fred_api_key:
            raise HTTPException(status_code=503, detail="FRED API key not configured")
        
        async with httpx.AsyncClient() as client:
            # Get historical item prices
            fred_url = f"https://api.stlouisfed.org/fred/series/observations"
            fred_params = {
                "series_id": fred_series,
                "api_key": fred_api_key,
                "file_type": "json",
                "observation_start": from_date,
                "observation_end": to_date,
                "frequency": "m"  # Monthly data
            }
            
            # Get historical BTC prices (simplified - using current price as proxy)
            # In production, you'd want actual historical BTC data
            btc_price = await get_btc_price()
            
            fred_response = await client.get(fred_url, params=fred_params, timeout=15.0)
            fred_response.raise_for_status()
            fred_data = fred_response.json()
            
            observations = fred_data.get("observations", [])
            
            dates = []
            btc_prices = []
            
            for obs in observations:
                if obs["value"] != ".":  # FRED uses "." for missing data
                    dates.append(obs["date"])
                    # Calculate BTC price needed to buy this item at this time
                    # This is simplified - real implementation would use historical BTC prices
                    item_price_usd = float(obs["value"])
                    btc_equivalent = item_price_usd / btc_price
                    btc_prices.append(round(btc_equivalent, 8))
            
            return HistoricalResponse(dates=dates, btc_prices=btc_prices)
            
    except ValueError as e:
        if "time data" in str(e):
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        raise HTTPException(status_code=400, detail=str(e))
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout fetching historical data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Historical data error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 