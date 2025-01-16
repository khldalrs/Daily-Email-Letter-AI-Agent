import os
import requests
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def get_btc_price():
    """
    Fetches the current Bitcoin price in USD using the CoinGecko API.
    
    Returns:
        float: Current BTC price in USD
        None: If there's an error fetching the price
    """
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin",
            "vs_currencies": "usd"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data["bitcoin"]["usd"]
        
    except (requests.RequestException, KeyError) as e:
        print(f"Error fetching BTC price: {e}")
        return None

def store_price_in_supabase(price):
    """
    Stores the BTC price in Supabase database.
    
    Args:
        price (float): The current BTC price in USD
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        data = {
            "price": price,
            "created_at": datetime.utcnow().isoformat()
        }
        
        supabase.table('btc_prices').insert(data).execute()
        return True
        
    except Exception as e:
        print(f"Error storing price in database: {e}")
        return False

def main():
    # Fetch BTC price
    price = get_btc_price()
    
    if price:
        print(f"Current Bitcoin price: ${price:,.2f} USD")
        
        # Store in Supabase
        if store_price_in_supabase(price):
            print("Successfully stored price in database")
        else:
            print("Failed to store price in database")
    else:
        print("Failed to fetch Bitcoin price")

if __name__ == "__main__":
    main()
