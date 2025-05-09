import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from requests.exceptions import RequestException, Timeout, JSONDecodeError

load_dotenv()

API_KEY = os.getenv('API_RAINFOREST_KEY')
print(f"API Key: {os.getenv('API_RAINFOREST_KEY')}")
def search_amazon_products(search_term):
    try:
        url = 'https://api.rainforestapi.com/request'

        params= {
            'api_key': API_KEY,
            'type': 'search',
            'amazon_domain': 'amazon.com',
            'search_term': search_term,
            
        }


        response = requests.get(url, params=params)

        # print(f"Rainforest response status: {response.status_code}")
        # print(f"Rainforest response body: {response.text}")

        response.raise_for_status()  # Will throw if 4xx/5xx
        data = response.json()
        
        results = []
        for product in data.get("search_results", []):
            title = product['title']
            price = product.get('price', {}).get('value')

            # Extract image URL - handles multiple possible fields
            image_url = (
                product.get('image') or  # Primary image field
                product.get('main_image', {}).get('link') or  # Nested image field
                product.get('images', [{}])[0].get('link')  # First image in array
            )
            results.append({
                'title': title,
                'price': price,
                'image': image_url  # Add image URL to results
            })
        return results
    except JSONDecodeError:
            return {"error": "Invalid API response format"}, 502
    except RequestException as e:
        return {"error": f"API request failed: {str(e)}"}, 502


