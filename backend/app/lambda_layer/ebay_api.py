import os
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv

load_dotenv()

# eBay API credentials
EBAY_APP_ID = os.getenv('EBAY_APP_ID')
EBAY_CERT_ID = os.getenv('EBAY_CERT_ID')
print(f"API Key: {os.getenv('API_RAINFOREST_KEY')}")
print(f"API Key: {os.getenv('EBAY_APP_ID')}")
print(f"API Key: {os.getenv('EBAY_CERT_ID')}")


EBAY_SANDBOX_URL = "https://api.sandbox.ebay.com"

def get_ebay_oauth_token():
    """Get OAuth token for eBay Sandbox API"""
    try:
        response = requests.post(
            f"{EBAY_SANDBOX_URL}/identity/v1/oauth2/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "client_credentials",
                "scope": "https://api.ebay.com/oauth/api_scope",
            },
            auth=(EBAY_APP_ID, EBAY_CERT_ID)
        )
        response.raise_for_status()
        return response.json()['access_token']
    except RequestException as e:
        raise Exception(f"Failed to get eBay OAuth token: {str(e)}")

def search_ebay_products(search_term):
    """Search eBay Sandbox for products"""
    try:
        token = get_ebay_oauth_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY-US"  # US marketplace
        }
        
        params = {
            "q": search_term,
            "limit": "5",  # Limit to 5 results for sandbox
            "sort": "price"  # Sort by price
        }
        
        response = requests.get(
            f"{EBAY_SANDBOX_URL}/buy/browse/v1/item_summary/search",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        
        # Transform eBay response to match your Amazon format
        results = []
        for item in response.json().get('itemSummaries', []):
                        
            results.append({
                'title': item.get('title'),
                'price': float(item.get('price', {}).get('value', 0)),
                'image': item.get('image', {}).get('imageUrl'),
                'url': item.get('itemWebUrl'),
                'platform': 'eBay'  # Add platform identifier
            })
        
        return results
        
    except RequestException as e:
        raise Exception(f"eBay API request failed: {str(e)}")