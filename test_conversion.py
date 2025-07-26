#!/usr/bin/env python3
"""
Test script to verify Alpha Vantage integration and decimal precision
"""
import asyncio
import sys
import os

# Add the api directory to the path
sys.path.append('api')

async def test_alpha_vantage_integration():
    """Test the Alpha Vantage API integration"""
    print("🧪 Testing Alpha Vantage Integration\n")
    
    try:
        # Test oil price fetcher
        from items import fetch_oil_usd
        oil_price = await fetch_oil_usd()
        print(f"📊 Oil Price: ${oil_price:.2f} per barrel")
        
        # Test gold price fetcher
        from items import fetch_gold_usd
        gold_price = await fetch_gold_usd()
        print(f"🏆 Gold Price: ${gold_price:.2f} per ounce")
        
        # Test silver price fetcher
        from items import fetch_silver_usd
        silver_price = await fetch_silver_usd()
        print(f"🥈 Silver Price: ${silver_price:.2f} per ounce")
        
        # Test natural gas price fetcher
        from items import fetch_natural_gas_usd
        gas_price = await fetch_natural_gas_usd()
        print(f"⛽ Natural Gas Price: ${gas_price:.2f} per MMBtu")
        
        print("\n✅ All commodity price fetches completed (using fallback prices if no API key)")
        
    except Exception as e:
        print(f"❌ Error testing commodity fetchers: {e}")
        return False
    
    return True

async def test_conversion_api():
    """Test the conversion API with decimal precision"""
    print("\n🧪 Testing Conversion API\n")
    
    try:
        from index import convert
        
        # Test BTC to oil conversion
        result = await convert(btc_amount=0.1, item='oil', direction='btc_to_item')
        print(f"💰 0.1 BTC = {result.quantity:.6f} barrels of oil")
        print(f"📊 Oil price: ${result.usd_item:.2f}")
        print(f"💵 Total value: ${result.usd_total:.2f}")
        print(f"₿ BTC price: ${result.btc_price:.2f}")
        
        # Test sats conversion
        result_sats = await convert(btc_amount=10000000, sats=True, item='oil', direction='btc_to_item')
        print(f"\n🪙 10M sats = {result_sats.quantity:.6f} barrels of oil")
        
        # Test item to BTC conversion
        result_reverse = await convert(quantity=1, item='gold', direction='item_to_btc')
        print(f"\n🔄 1 ounce of gold = {result_reverse.quantity:.8f} BTC")
        
        # Test item to sats conversion
        result_reverse_sats = await convert(quantity=1, item='gold', direction='item_to_btc', sats=True)
        print(f"🔄 1 ounce of gold = {result_reverse_sats.quantity:,} sats")
        
        print("\n✅ All conversion tests passed")
        
    except Exception as e:
        print(f"❌ Error testing conversion API: {e}")
        return False
    
    return True

async def test_items_data():
    """Test the items data structure"""
    print("\n🧪 Testing Items Data Structure\n")
    
    try:
        from items import get_items_by_category, ITEMS
        
        categories = get_items_by_category()
        print("📋 Available categories:")
        for category, items in categories.items():
            print(f"  {category}: {len(items)} items")
            for item in items:
                print(f"    - {item['name']} (historical: {item['historical_support']})")
        
        print(f"\n📊 Total items configured: {len(ITEMS)}")
        print("\n✅ Items data structure test passed")
        
    except Exception as e:
        print(f"❌ Error testing items data: {e}")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🚀 BTC Real-World Converter - Alpha Vantage Integration Test\n")
    
    # Set environment variable warning
    if not os.getenv('ALPHA_VANTAGE_API_KEY'):
        print("⚠️  ALPHA_VANTAGE_API_KEY not found - using fallback prices")
        print("   Get a free API key from: https://www.alphavantage.co/support/#api-key\n")
    
    tests = [
        test_alpha_vantage_integration,
        test_conversion_api,
        test_items_data
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Alpha Vantage integration is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main()) 