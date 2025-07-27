#!/usr/bin/env python3
"""
Debug script to test environment variables and API functionality
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_env_vars():
    """Check if environment variables are loaded correctly"""
    print("🔍 Checking Environment Variables...\n")
    
    # Check for .env file
    env_file_exists = os.path.exists('.env')
    print(f"📁 .env file exists: {'✅ Yes' if env_file_exists else '❌ No'}")
    
    if env_file_exists:
        try:
            with open('.env', 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
                print(f"📄 .env file has {len(lines)} non-comment lines")
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
    
    # Check environment variables
    env_vars = {
        'ALPHA_VANTAGE_API_KEY': os.getenv('ALPHA_VANTAGE_API_KEY'),
        'FRED_API_KEY': os.getenv('FRED_API_KEY'),
        'BLS_API_KEY': os.getenv('BLS_API_KEY')
    }
    
    print("\n🔑 Environment Variables Status:")
    for var_name, var_value in env_vars.items():
        if var_value:
            masked_value = var_value[:4] + "*" * (len(var_value) - 8) + var_value[-4:] if len(var_value) > 8 else "****"
            print(f"  {var_name}: ✅ Set ({masked_value})")
        else:
            print(f"  {var_name}: ❌ Not set")
    
    return all(var_value for var_value in env_vars.values())

async def test_api_calls():
    """Test actual API calls to verify keys work"""
    print("\n🧪 Testing API Calls...\n")
    
    # Add the api directory to the path
    sys.path.append('api')
    
    try:
        # Test Alpha Vantage - Oil
        print("🛢️  Testing Alpha Vantage (Oil)...")
        from items import fetch_oil_usd
        oil_price = await fetch_oil_usd()
        if oil_price != 75.0:  # Not the fallback price
            print(f"   ✅ Success: ${oil_price:.2f} per barrel")
        else:
            print(f"   ⚠️  Using fallback price: ${oil_price:.2f} (API key might be invalid)")
        
        # Test Alpha Vantage - Gold
        print("🏆 Testing Alpha Vantage (Gold)...")
        from items import fetch_gold_usd
        gold_price = await fetch_gold_usd()
        if gold_price != 2000.0:  # Not the fallback price
            print(f"   ✅ Success: ${gold_price:.2f} per ounce")
        else:
            print(f"   ⚠️  Using fallback price: ${gold_price:.2f} (API key might be invalid)")
        
        # Test FRED - Bread
        print("🍞 Testing FRED API (Bread)...")
        from items import fetch_bread_usd
        bread_price = await fetch_bread_usd()
        if bread_price != 2.50:  # Not the fallback price
            print(f"   ✅ Success: ${bread_price:.2f} per loaf")
        else:
            print(f"   ⚠️  Using fallback price: ${bread_price:.2f} (API key might be invalid)")
        
    except Exception as e:
        print(f"❌ Error testing APIs: {e}")
        return False
    
    return True

async def test_conversion():
    """Test the conversion functionality"""
    print("\n💱 Testing Conversion API...\n")
    
    try:
        from index import convert
        
        # Test conversion with oil
        result = await convert(btc_amount=0.1, item='oil', direction='btc_to_item')
        print(f"💰 Conversion Test: 0.1 BTC = {result.quantity:.2f} barrels of oil")
        print(f"   Oil price: ${result.usd_item:.2f}")
        print(f"   BTC price: ${result.btc_price:.2f}")
        print(f"   Total value: ${result.usd_total:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing conversion: {e}")
        return False

def show_setup_instructions():
    """Show instructions for setting up API keys"""
    print("\n📋 Setup Instructions:")
    print("\n1. Edit the .env file in this directory:")
    print("   nano .env")
    print("\n2. Replace the placeholder values with your actual API keys:")
    print("   ALPHA_VANTAGE_API_KEY=your_actual_alpha_vantage_key")
    print("   FRED_API_KEY=your_actual_fred_key")
    print("   BLS_API_KEY=your_actual_bls_key")
    print("\n3. Save the file and run this debug script again")
    print("\n🔗 Get your API keys:")
    print("   • Alpha Vantage: https://www.alphavantage.co/support/#api-key")
    print("   • FRED: https://api.stlouisfed.org/")
    print("   • BLS: https://www.bls.gov/developers/")

async def main():
    """Main debug function"""
    print("🚀 BTC Real-World Converter - Environment Debug Tool\n")
    
    # Check environment variables
    env_ok = check_env_vars()
    
    if not env_ok:
        print("\n❌ Some environment variables are missing!")
        show_setup_instructions()
        return 1
    
    # Test API calls
    api_ok = await test_api_calls()
    
    # Test conversion
    conversion_ok = await test_conversion()
    
    # Summary
    print(f"\n📊 Debug Summary:")
    print(f"   Environment Variables: {'✅' if env_ok else '❌'}")
    print(f"   API Calls: {'✅' if api_ok else '❌'}")
    print(f"   Conversion: {'✅' if conversion_ok else '❌'}")
    
    if env_ok and api_ok and conversion_ok:
        print("\n🎉 Everything looks good! Your API keys are working correctly.")
        print("   You can now run the app with: uvicorn api.index:app --reload")
    else:
        print("\n❌ Some issues found. Check the output above and fix them.")
        if not env_ok:
            show_setup_instructions()
    
    return 0 if (env_ok and api_ok and conversion_ok) else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main()) 