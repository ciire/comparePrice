import json
from datetime import timedelta
from redis.exceptions import ConnectionError
from app.db.redis_client import redis_client
from app.lambda_layer.ebay_api import search_ebay_products

def search_results(search_term: str) -> dict:
    cache_key = f"search:{search_term}"

    try:
        cached_results = redis_client.get(cache_key)
        if cached_results:
            return json.loads(cached_results.decode("utf-8"))
    except ConnectionError:
        pass  # Redis down, proceed without cache

    # Call API
    ebay_results = search_ebay_products(search_term)

    combined_results = {
        # "amazon": amazon_results,
        "ebay": ebay_results
    }

    try:
        redis_client.setex(cache_key, timedelta(hours=1), json.dumps(combined_results))
    except ConnectionError:
        pass

    return combined_results
