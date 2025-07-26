import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from decimal import Decimal

# Test the Alpha Vantage integration
class TestAlphaVantageIntegration:
    
    @pytest.fixture
    def mock_alpha_vantage_response(self):
        """Mock Alpha Vantage API response for commodities"""
        return {
            "data": [
                {"date": "2024-01-26", "value": "75.50"}
            ]
        }
    
    @pytest.fixture
    def mock_alpha_vantage_currency_response(self):
        """Mock Alpha Vantage currency exchange response"""
        return {
            "Realtime Currency Exchange Rate": {
                "1. From_Currency Code": "USD",
                "2. From_Currency Name": "United States Dollar",
                "3. To_Currency Code": "XAU",
                "4. To_Currency Name": "Gold Ounce",
                "5. Exchange Rate": "0.0005000",
                "6. Last Refreshed": "2024-01-26 15:30:01",
                "7. Time Zone": "UTC",
                "8. Bid Price": "0.0004999",
                "9. Ask Price": "0.0005001"
            }
        }

    @pytest.mark.asyncio
    async def test_fetch_oil_usd_success(self, mock_alpha_vantage_response):
        """Test successful oil price fetch from Alpha Vantage"""
        with patch('api.items.httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_alpha_vantage_response
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with patch('api.items.os.getenv', return_value='test_api_key'):
                from api.items import fetch_oil_usd
                price = await fetch_oil_usd()
                assert price == 75.50

    @pytest.mark.asyncio
    async def test_fetch_gold_usd_success(self, mock_alpha_vantage_currency_response):
        """Test successful gold price fetch from Alpha Vantage"""
        with patch('api.items.httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_alpha_vantage_currency_response
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with patch('api.items.os.getenv', return_value='test_api_key'):
                from api.items import fetch_gold_usd
                price = await fetch_gold_usd()
                # 1 / 0.0005 = 2000
                assert price == 2000.0

    @pytest.mark.asyncio
    async def test_fetch_oil_usd_no_api_key(self):
        """Test oil price fetch fallback when no API key"""
        with patch('api.items.os.getenv', return_value=None):
            from api.items import fetch_oil_usd
            price = await fetch_oil_usd()
            assert price == 75.0  # Fallback price

    @pytest.mark.asyncio
    async def test_fetch_oil_usd_api_error(self):
        """Test oil price fetch fallback on API error"""
        error_response = {"Error Message": "Invalid API call"}
        
        with patch('api.items.httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = error_response
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with patch('api.items.os.getenv', return_value='test_api_key'):
                from api.items import fetch_oil_usd
                price = await fetch_oil_usd()
                assert price == 75.0  # Fallback price

    @pytest.mark.asyncio
    async def test_fetch_gold_usd_rate_limit(self):
        """Test gold price fetch fallback on rate limit"""
        rate_limit_response = {"Note": "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute"}
        
        with patch('api.items.httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = rate_limit_response
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with patch('api.items.os.getenv', return_value='test_api_key'):
                from api.items import fetch_gold_usd
                price = await fetch_gold_usd()
                assert price == 2000.0  # Fallback price

    def test_decimal_precision_conversion(self):
        """Test that conversion calculations use proper decimal precision"""
        from api.index import ConvertResponse
        from decimal import Decimal
        
        # Simulate conversion calculation
        btc_amount = Decimal('0.1')
        btc_price = Decimal('50000.123456')
        item_price = Decimal('2.567891')
        
        usd_total = btc_amount * btc_price
        item_quantity = usd_total / item_price
        
        # Test proper quantization
        quantity_result = float(item_quantity.quantize(Decimal('0.000001')))
        usd_item_result = float(item_price.quantize(Decimal('0.01')))
        usd_total_result = float(usd_total.quantize(Decimal('0.01')))
        btc_price_result = float(btc_price.quantize(Decimal('0.01')))
        
        assert isinstance(quantity_result, float)
        assert isinstance(usd_item_result, float)
        assert isinstance(usd_total_result, float)
        assert isinstance(btc_price_result, float)
        
        # Check that values are properly rounded
        assert usd_item_result == 2.57  # Rounded to 2 decimal places
        assert btc_price_result == 50000.12  # Rounded to 2 decimal places

if __name__ == "__main__":
    pytest.main([__file__]) 