# BTC Real-World Converter

## Overview
Web app to convert BTC/sats to equivalent goods/services quantities using real-time prices. Lean stack: FastAPI backend for API proxy/computes, vanilla JS frontend for UI.

## Features
- ⚡ Real-time BTC to goods conversion
- 🔄 Bidirectional conversion (BTC → Items or Items → BTC)
- 📊 Historical price charts for CPI items
- 📱 Responsive design for mobile and desktop
- 🌐 Multiple data sources (CoinGecko, FRED, BLS, Commodities API)
- ⚙️ Unit toggle (BTC/sats)
- 🎯 15+ items across categories (Food, Energy, Housing, etc.)

## Setup

### Local Development

1. **Clone and install dependencies:**
   ```bash
   git clone <repository-url>
   cd pricing-bitcoin
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file with your API keys:
   ```env
   # Required for commodities data (Oil, Gold, Silver, Natural Gas)
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
   
   # Required for historical CPI data
   FRED_API_KEY=your_fred_api_key_here
   
   # Optional for BLS data
   BLS_API_KEY=your_bls_api_key_here
   ```

3. **Get API Keys:**
   - **Alpha Vantage API**: [Get free key](https://www.alphavantage.co/support/#api-key) (5 calls/minute, 500 calls/day free)
   - **FRED API**: [Get free key](https://api.stlouisfed.org/) (unlimited requests)
   - **BLS API**: [Get free key](https://www.bls.gov/developers/) (optional, has fallbacks)

4. **Run locally:**
   ```bash
   uvicorn main:app --reload
   ```
   Visit [http://localhost:8000](http://localhost:8000)

### Deployment

**Vercel (Recommended):**
1. Push to GitHub
2. Connect repository to Vercel
3. Add environment variables in Vercel dashboard
4. Deploy automatically

**Other platforms:**
- Works on any platform supporting Python/FastAPI
- Ensure static files are served correctly

## Architecture

```
├── main.py              # FastAPI app with /api/convert and /api/historical endpoints
├── items.py             # Item configurations and API fetcher functions
├── static/
│   ├── index.html       # Main UI with converter and charts
│   ├── script.js        # Frontend logic with debouncing and API calls
│   └── style.css        # Responsive styling
├── requirements.txt     # Python dependencies
├── vercel.json         # Deployment configuration
└── README.md           # This file
```

## API Endpoints

### `GET /api/convert`
Convert between BTC and item quantities.

**Parameters:**
- `item` (required): Item identifier (e.g., 'bread', 'oil', 'gold')
- `direction` (required): 'btc_to_item' or 'item_to_btc'
- `btc_amount` (conditional): Required if direction is 'btc_to_item'
- `quantity` (conditional): Required if direction is 'item_to_btc'
- `sats` (optional): Boolean, use satoshis instead of BTC

**Response:**
```json
{
  "quantity": 5.3,
  "usd_item": 75.0,
  "usd_total": 397.5,
  "btc_price": 42000.0
}
```

### `GET /api/historical`
Get historical price data for CPI items.

**Parameters:**
- `item` (required): Item with historical support
- `from_date` (required): Start date (YYYY-MM-DD)
- `to_date` (required): End date (YYYY-MM-DD)

**Response:**
```json
{
  "dates": ["2023-01-01", "2023-02-01", ...],
  "btc_prices": [0.00012, 0.00015, ...]
}
```

## Available Items

### Energy
- Oil (barrel) - Alpha Vantage API (WTI crude oil)
- Natural Gas (MMBtu) - Alpha Vantage API
- Gasoline (gallon) - BLS API + historical support

### Commodities  
- Gold (ounce) - Alpha Vantage API (USD/XAU currency exchange)
- Silver (ounce) - Alpha Vantage API (USD/XAG currency exchange)

### Food
- Bread (loaf) - FRED API + historical support
- Milk (gallon) - FRED API + historical support
- Coffee (pound) - FRED API + historical support
- Eggs (dozen) - FRED API + historical support
- Big Mac (burger) - Static pricing

### Housing
- Median Home (house) - FRED API + historical support

### Transportation
- New Car (car) - FRED API + historical support
- Uber Ride (ride) - Static pricing

### Entertainment
- Netflix (month) - Static pricing
- Spotify (month) - Static pricing
- Movie Ticket (ticket) - Static pricing

## Technical Details

### Frontend
- **Vanilla JavaScript** - No heavy frameworks
- **Debounced inputs** - 300ms delay to reduce API calls
- **Responsive design** - Mobile-first CSS
- **Error handling** - Toast notifications for errors
- **Charts** - CanvasJS for historical data visualization

### Backend
- **FastAPI** - Modern Python web framework
- **Async/await** - Non-blocking API calls
- **Caching** - 5-minute BTC price cache
- **Validation** - Pydantic models for request/response
- **Error handling** - Proper HTTP status codes and messages

### Data Sources
- **Bitcoin Price**: CoinGecko API (no key required)
- **Commodities**: Alpha Vantage API (Oil via WTI, Gold/Silver via currency exchange rates)
- **Economic Data**: Federal Reserve Economic Data (FRED)
- **Labor Statistics**: Bureau of Labor Statistics (BLS)

## Contributing

Keep it lean—no extra dependencies. Use `int` for sats precision. Tests with pytest.

### Development Guidelines
1. **No heavy frameworks** - Keep frontend vanilla
2. **Fallback values** - Always provide fallbacks when APIs fail  
3. **Error handling** - Graceful degradation for network issues
4. **Caching** - Cache frequently accessed data
5. **Validation** - Validate all inputs client and server-side

## License

Apache 2.0 - see LICENSE file for details.

## Disclaimer

Prices are approximate and for educational purposes. Data from various APIs may have delays or inaccuracies. Not financial advice. 
