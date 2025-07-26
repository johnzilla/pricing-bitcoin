import httpx
import os
from typing import Dict, Any, Callable
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def fetch_oil_usd() -> float:
    """Fetch oil price from Alpha Vantage API (WTI crude oil)"""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("Warning: ALPHA_VANTAGE_API_KEY not found, using fallback price")
        return 75.0
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.alphavantage.co/query?function=WTI&interval=daily&apikey={api_key}",
                timeout=15.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                raise Exception(f"Alpha Vantage error: {data['Error Message']}")
            if "Note" in data:
                raise Exception(f"Alpha Vantage rate limit: {data['Note']}")
            
            # Get latest daily price
            if "data" in data and len(data["data"]) > 0:
                latest_price = float(data["data"][0]["value"])
                return latest_price
            else:
                raise Exception("No price data returned")
                
    except Exception as e:
        print(f"Error fetching oil price from Alpha Vantage: {e}")
        # Fallback to approximate current oil price
        return 75.0

async def fetch_gold_usd() -> float:
    """Fetch gold price from Alpha Vantage API (per ounce)"""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("Warning: ALPHA_VANTAGE_API_KEY not found, using fallback price")
        return 2000.0
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=XAU&apikey={api_key}",
                timeout=15.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                raise Exception(f"Alpha Vantage error: {data['Error Message']}")
            if "Note" in data:
                raise Exception(f"Alpha Vantage rate limit: {data['Note']}")
            
            # Get exchange rate and invert to get USD per ounce of gold
            if "Realtime Currency Exchange Rate" in data:
                exchange_rate = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
                # Invert the rate: if 1 USD = 0.0005 XAU, then 1 XAU = 2000 USD
                gold_price_usd = 1.0 / exchange_rate
                return gold_price_usd
            else:
                raise Exception("No exchange rate data returned")
                
    except Exception as e:
        print(f"Error fetching gold price from Alpha Vantage: {e}")
        return 2000.0

async def fetch_silver_usd() -> float:
    """Fetch silver price from Alpha Vantage API (per ounce)"""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("Warning: ALPHA_VANTAGE_API_KEY not found, using fallback price")
        return 25.0
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=XAG&apikey={api_key}",
                timeout=15.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                raise Exception(f"Alpha Vantage error: {data['Error Message']}")
            if "Note" in data:
                raise Exception(f"Alpha Vantage rate limit: {data['Note']}")
            
            # Get exchange rate and invert to get USD per ounce of silver
            if "Realtime Currency Exchange Rate" in data:
                exchange_rate = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
                # Invert the rate: if 1 USD = 0.04 XAG, then 1 XAG = 25 USD
                silver_price_usd = 1.0 / exchange_rate
                return silver_price_usd
            else:
                raise Exception("No exchange rate data returned")
                
    except Exception as e:
        print(f"Error fetching silver price from Alpha Vantage: {e}")
        return 25.0

async def fetch_natural_gas_usd() -> float:
    """Fetch natural gas price from Alpha Vantage API"""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("Warning: ALPHA_VANTAGE_API_KEY not found, using fallback price")
        return 3.50
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.alphavantage.co/query?function=NATURAL_GAS&interval=daily&apikey={api_key}",
                timeout=15.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                raise Exception(f"Alpha Vantage error: {data['Error Message']}")
            if "Note" in data:
                raise Exception(f"Alpha Vantage rate limit: {data['Note']}")
            
            # Get latest daily price
            if "data" in data and len(data["data"]) > 0:
                latest_price = float(data["data"][0]["value"])
                return latest_price
            else:
                raise Exception("No price data returned")
                
    except Exception as e:
        print(f"Error fetching natural gas price from Alpha Vantage: {e}")
        return 3.50

async def fetch_gasoline_usd() -> float:
    """Fetch gasoline price (using BLS API for US average)"""
    # BLS Series ID for gasoline prices
    series_id = "APU000074714"  # Average Price: Gasoline, all types (per gallon/3.785 liters)
    bls_api_key = os.getenv("BLS_API_KEY")
    
    try:
        if bls_api_key:
            async with httpx.AsyncClient() as client:
                headers = {"Content-type": "application/json"}
                data = {
                    "seriesid": [series_id],
                    "startyear": "2024",
                    "endyear": "2024",
                    "registrationkey": bls_api_key
                }
                response = await client.post(
                    "https://api.bls.gov/publicAPI/v2/timeseries/data/",
                    json=data,
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                
                if result["status"] == "REQUEST_SUCCEEDED" and result["Results"]:
                    latest_data = result["Results"]["series"][0]["data"][0]
                    return float(latest_data["value"])
        
        # Fallback: approximate current US gas price
        return 3.50
        
    except Exception:
        return 3.50

async def fetch_bread_usd() -> float:
    """Fetch bread price using FRED API"""
    fred_api_key = os.getenv("FRED_API_KEY")
    if not fred_api_key:
        return 2.50
    
    try:
        async with httpx.AsyncClient() as client:
            # FRED series for average price of bread
            response = await client.get(
                f"https://api.stlouisfed.org/fred/series/observations?series_id=APU0000702111&api_key={fred_api_key}&file_type=json&limit=1&sort_order=desc",
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            observations = data.get("observations", [])
            if observations and observations[0]["value"] != ".":
                return float(observations[0]["value"])
        
        return 2.50
        
    except Exception:
        return 2.50

async def fetch_milk_usd() -> float:
    """Fetch milk price using FRED API"""
    fred_api_key = os.getenv("FRED_API_KEY")
    if not fred_api_key:
        return 3.80
    
    try:
        async with httpx.AsyncClient() as client:
            # FRED series for average price of milk
            response = await client.get(
                f"https://api.stlouisfed.org/fred/series/observations?series_id=APU0000709112&api_key={fred_api_key}&file_type=json&limit=1&sort_order=desc",
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            observations = data.get("observations", [])
            if observations and observations[0]["value"] != ".":
                return float(observations[0]["value"])
        
        return 3.80
        
    except Exception:
        return 3.80

async def fetch_coffee_usd() -> float:
    """Fetch coffee price using FRED API"""
    fred_api_key = os.getenv("FRED_API_KEY")
    if not fred_api_key:
        return 4.50
    
    try:
        async with httpx.AsyncClient() as client:
            # FRED series for average price of coffee
            response = await client.get(
                f"https://api.stlouisfed.org/fred/series/observations?series_id=APU0000717311&api_key={fred_api_key}&file_type=json&limit=1&sort_order=desc",
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            observations = data.get("observations", [])
            if observations and observations[0]["value"] != ".":
                return float(observations[0]["value"])
        
        return 4.50
        
    except Exception:
        return 4.50

async def fetch_eggs_usd() -> float:
    """Fetch eggs price using FRED API"""
    fred_api_key = os.getenv("FRED_API_KEY")
    if not fred_api_key:
        return 2.20
    
    try:
        async with httpx.AsyncClient() as client:
            # FRED series for average price of eggs
            response = await client.get(
                f"https://api.stlouisfed.org/fred/series/observations?series_id=APU0000708111&api_key={fred_api_key}&file_type=json&limit=1&sort_order=desc",
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            observations = data.get("observations", [])
            if observations and observations[0]["value"] != ".":
                return float(observations[0]["value"])
        
        return 2.20
        
    except Exception:
        return 2.20

async def fetch_median_home_usd() -> float:
    """Fetch median home price using FRED API"""
    fred_api_key = os.getenv("FRED_API_KEY")
    if not fred_api_key:
        return 420000.0
    
    try:
        async with httpx.AsyncClient() as client:
            # FRED series for median home price
            response = await client.get(
                f"https://api.stlouisfed.org/fred/series/observations?series_id=MSPUS&api_key={fred_api_key}&file_type=json&limit=1&sort_order=desc",
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            observations = data.get("observations", [])
            if observations and observations[0]["value"] != ".":
                return float(observations[0]["value"])
        
        return 420000.0
        
    except Exception:
        return 420000.0

async def fetch_big_mac_usd() -> float:
    """Fetch Big Mac price (approximate)"""
    # Big Mac price is relatively stable, using approximate current price
    return 5.50

async def fetch_netflix_usd() -> float:
    """Netflix subscription price (standard plan)"""
    return 15.49

async def fetch_spotify_usd() -> float:
    """Spotify premium subscription price"""
    return 10.99

async def fetch_uber_ride_usd() -> float:
    """Average Uber ride price (5 mile trip)"""
    return 15.00

async def fetch_movie_ticket_usd() -> float:
    """Average movie ticket price"""
    return 12.00

async def fetch_new_car_usd() -> float:
    """Average new car price using FRED API"""
    fred_api_key = os.getenv("FRED_API_KEY")
    if not fred_api_key:
        return 48000.0
    
    try:
        async with httpx.AsyncClient() as client:
            # FRED series for average price of new vehicles
            response = await client.get(
                f"https://api.stlouisfed.org/fred/series/observations?series_id=CUSR0000SETA01&api_key={fred_api_key}&file_type=json&limit=1&sort_order=desc",
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            observations = data.get("observations", [])
            if observations and observations[0]["value"] != ".":
                # This is a CPI index, convert to approximate dollar amount
                index_value = float(observations[0]["value"])
                # Using base year calculation to approximate current price
                return (index_value / 100) * 48000.0
        
        return 48000.0
        
    except Exception:
        return 48000.0

# Items configuration with categories, units, and fetcher functions
ITEMS: Dict[str, Dict[str, Any]] = {
    "oil": {
        "category": "Energy",
        "unit": "barrel",
        "fetcher": fetch_oil_usd,
        "historical_support": False
    },
    "gasoline": {
        "category": "Energy",
        "unit": "gallon",
        "fetcher": fetch_gasoline_usd,
        "historical_support": True,
        "fred_series": "APU000074714"
    },
    "natural_gas": {
        "category": "Energy",
        "unit": "MMBtu",
        "fetcher": fetch_natural_gas_usd,
        "historical_support": False
    },
    "gold": {
        "category": "Commodities",
        "unit": "ounce",
        "fetcher": fetch_gold_usd,
        "historical_support": False
    },
    "silver": {
        "category": "Commodities",
        "unit": "ounce",
        "fetcher": fetch_silver_usd,
        "historical_support": False
    },
    "bread": {
        "category": "Food",
        "unit": "loaf",
        "fetcher": fetch_bread_usd,
        "historical_support": True,
        "fred_series": "APU0000702111"
    },
    "milk": {
        "category": "Food",
        "unit": "gallon",
        "fetcher": fetch_milk_usd,
        "historical_support": True,
        "fred_series": "APU0000709112"
    },
    "coffee": {
        "category": "Food",
        "unit": "pound",
        "fetcher": fetch_coffee_usd,
        "historical_support": True,
        "fred_series": "APU0000717311"
    },
    "eggs": {
        "category": "Food",
        "unit": "dozen",
        "fetcher": fetch_eggs_usd,
        "historical_support": True,
        "fred_series": "APU0000708111"
    },
    "big_mac": {
        "category": "Food",
        "unit": "burger",
        "fetcher": fetch_big_mac_usd,
        "historical_support": False
    },
    "median_home": {
        "category": "Housing",
        "unit": "house",
        "fetcher": fetch_median_home_usd,
        "historical_support": True,
        "fred_series": "MSPUS"
    },
    "new_car": {
        "category": "Transportation",
        "unit": "car",
        "fetcher": fetch_new_car_usd,
        "historical_support": True,
        "fred_series": "CUSR0000SETA01"
    },
    "uber_ride": {
        "category": "Transportation",
        "unit": "ride",
        "fetcher": fetch_uber_ride_usd,
        "historical_support": False
    },
    "netflix": {
        "category": "Entertainment",
        "unit": "month",
        "fetcher": fetch_netflix_usd,
        "historical_support": False
    },
    "spotify": {
        "category": "Entertainment",
        "unit": "month",
        "fetcher": fetch_spotify_usd,
        "historical_support": False
    },
    "movie_ticket": {
        "category": "Entertainment",
        "unit": "ticket",
        "fetcher": fetch_movie_ticket_usd,
        "historical_support": False
    }
}

def get_item_fetcher(item_name: str) -> Callable:
    """Get the fetcher function for a specific item"""
    if item_name not in ITEMS:
        raise ValueError(f"Item '{item_name}' not found")
    return ITEMS[item_name]["fetcher"]

def get_items_by_category() -> Dict[str, list]:
    """Group items by category for frontend dropdown"""
    categories = {}
    for item_key, item_info in ITEMS.items():
        category = item_info["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append({
            "key": item_key,
            "name": f"{item_key.replace('_', ' ').title()} ({item_info['unit']})",
            "unit": item_info["unit"],
            "historical_support": item_info.get("historical_support", False)
        })
    return categories 