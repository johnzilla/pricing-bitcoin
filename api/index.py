from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from decimal import Decimal
import httpx
import os
from typing import Optional, List
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import items module
try:
    from items import ITEMS, get_item_fetcher, get_items_by_category
except ImportError:
    # Fallback items for deployment
    ITEMS = {
        "bread": {"category": "Food", "unit": "loaf", "fetcher": lambda: 2.50, "historical_support": True},
        "oil": {"category": "Energy", "unit": "barrel", "fetcher": lambda: 75.0, "historical_support": False},
        "natural_gas": {"category": "Energy", "unit": "MMBtu", "fetcher": lambda: 3.50, "historical_support": False},
        "gold": {"category": "Commodities", "unit": "ounce", "fetcher": lambda: 2000.0, "historical_support": False},
        "silver": {"category": "Commodities", "unit": "ounce", "fetcher": lambda: 25.0, "historical_support": False},
        "milk": {"category": "Food", "unit": "gallon", "fetcher": lambda: 3.80, "historical_support": True}
    }
    def get_items_by_category():
        return {
            "Food": [
                {"key": "bread", "name": "Bread (loaf)", "unit": "loaf", "historical_support": True},
                {"key": "milk", "name": "Milk (gallon)", "unit": "gallon", "historical_support": True}
            ],
            "Energy": [
                {"key": "oil", "name": "Oil (barrel)", "unit": "barrel", "historical_support": False},
                {"key": "natural_gas", "name": "Natural Gas (MMBtu)", "unit": "MMBtu", "historical_support": False}
            ],
            "Commodities": [
                {"key": "gold", "name": "Gold (ounce)", "unit": "ounce", "historical_support": False},
                {"key": "silver", "name": "Silver (ounce)", "unit": "ounce", "historical_support": False}
            ]
        }
    def get_item_fetcher(item): 
        prices = {"bread": 2.50, "oil": 75.0, "natural_gas": 3.50, "gold": 2000.0, "silver": 25.0, "milk": 3.80}
        return lambda: prices.get(item, 10.0)

app = FastAPI()

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
        return 50000.0  # Fallback price

@app.get("/")
async def serve_index():
    """Serve the main HTML page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BTC Real-World Converter</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; font-weight: 600; color: #555; }
            input, select, button { padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 16px; width: 200px; }
            button { background: #667eea; color: white; border: none; cursor: pointer; width: auto; padding: 12px 24px; }
            button:hover { background: #5a6fd8; }
            .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 BTC Real-World Converter</h1>
            <div class="form-group">
                <label>Bitcoin Amount:</label>
                <input type="number" id="btc-input" placeholder="0.1" step="any">
            </div>
            <div class="form-group">
                <label>Item:</label>
                                 <select id="item-select">
                     <option value="">Select an item...</option>
                     <optgroup label="Food">
                         <option value="bread">Bread (loaf)</option>
                         <option value="milk">Milk (gallon)</option>
                     </optgroup>
                     <optgroup label="Energy">
                         <option value="oil">Oil (barrel)</option>
                         <option value="natural_gas">Natural Gas (MMBtu)</option>
                     </optgroup>
                     <optgroup label="Commodities">
                         <option value="gold">Gold (ounce)</option>
                         <option value="silver">Silver (ounce)</option>
                     </optgroup>
                 </select>
            </div>
            <button onclick="convert()">Convert</button>
            <div id="result" class="result" style="display:none;"></div>
        </div>
        <script>
            async function convert() {
                const btcAmount = document.getElementById('btc-input').value;
                const item = document.getElementById('item-select').value;
                
                if (!btcAmount || !item) {
                    alert('Please enter BTC amount and select an item');
                    return;
                }
                
                                 try {
                     const response = await fetch(`/api/convert?btc_amount=${btcAmount}&item=${item}&direction=btc_to_item`);
                     
                     if (!response.ok) {
                         throw new Error(`API Error: ${response.status} ${response.statusText}`);
                     }
                     
                     const data = await response.json();
                     
                     // Check if the API returned an error
                     if (data.detail) {
                         throw new Error(data.detail);
                     }
                     
                     console.log('Conversion successful:', data);
                     
                     document.getElementById('result').innerHTML = `
                         <strong>Result:</strong> ${data.quantity.toLocaleString()} ${item}(s)<br>
                         <strong>Item Price:</strong> $${data.usd_item.toLocaleString()}<br>
                         <strong>Total Value:</strong> $${data.usd_total.toLocaleString()}<br>
                         <strong>BTC Price:</strong> $${data.btc_price.toLocaleString()}
                     `;
                     document.getElementById('result').style.display = 'block';
                 } catch (error) {
                     console.error('Conversion error:', error);
                     const errorMsg = error.message.includes('rate limit') ? 
                         'API rate limit reached. Please try again later.' :
                         error.message.includes('API Error') ?
                         'API service temporarily unavailable. Please try again later.' :
                         'Error: ' + error.message;
                     
                     alert(errorMsg);
                     document.getElementById('result').style.display = 'none';
                 }
            }
        </script>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

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
        # Get BTC price and item price
        btc_price = await get_btc_price()
        
        # Try to get item price from fetcher, fallback to hardcoded prices
        try:
            item_fetcher = get_item_fetcher(item)
            item_price_raw = await item_fetcher() if asyncio.iscoroutinefunction(item_fetcher) else item_fetcher()
            item_price = float(Decimal(str(item_price_raw)).quantize(Decimal('0.01')))
        except Exception as e:
            print(f"Error fetching price for {item}: {e}")
            # Fallback hardcoded prices
            item_prices = {"bread": 2.50, "oil": 75.0, "natural_gas": 3.50, "gold": 2000.0, "silver": 25.0, "milk": 3.80}
            item_price = item_prices.get(item, 10.0)
        
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
            
            # Calculate quantities using Decimal precision
            btc_price_decimal = Decimal(str(btc_price))
            item_price_decimal = Decimal(str(item_price))
            usd_total_decimal = btc_value * btc_price_decimal
            item_quantity_decimal = usd_total_decimal / item_price_decimal
            
            return ConvertResponse(
                quantity=float(item_quantity_decimal.quantize(Decimal('0.000001'))),
                usd_item=float(item_price_decimal.quantize(Decimal('0.01'))),
                usd_total=float(usd_total_decimal.quantize(Decimal('0.01'))),
                btc_price=float(btc_price_decimal.quantize(Decimal('0.01')))
            )
        
        else:  # item_to_btc
            # Validate quantity
            if quantity is None:
                raise HTTPException(status_code=400, detail="quantity is required for item_to_btc conversion")
            
            if quantity <= 0:
                raise HTTPException(status_code=400, detail="Quantity must be positive")
            
            # Calculate BTC needed using Decimal precision
            quantity_decimal = Decimal(str(quantity))
            item_price_decimal = Decimal(str(item_price))
            btc_price_decimal = Decimal(str(btc_price))
            usd_total_decimal = quantity_decimal * item_price_decimal
            btc_needed_decimal = usd_total_decimal / btc_price_decimal
            
            # Convert to sats if requested
            if sats:
                btc_needed_decimal = btc_needed_decimal * Decimal("100000000")  # Convert BTC to sats
                final_quantity = int(btc_needed_decimal.quantize(Decimal('1')))  # Integer sats
            else:
                final_quantity = float(btc_needed_decimal.quantize(Decimal('0.00000001')))  # 8 decimal places for BTC
            
            return ConvertResponse(
                quantity=final_quantity,
                usd_item=float(item_price_decimal.quantize(Decimal('0.01'))),
                usd_total=float(usd_total_decimal.quantize(Decimal('0.01'))),
                btc_price=float(btc_price_decimal.quantize(Decimal('0.01')))
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")

# For Vercel compatibility
handler = app 