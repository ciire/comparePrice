import json
from flask import Flask, jsonify, request
import os
from flask_cors import CORS
import redis
from datetime import timedelta
from app.db.mongo_client import db
from app.db.indexes import setup_indexes
from app.controllers.userController import signup_user_controller, edit_user_controller, verify_signup_code_controller
from app.controllers.userController import send_verification_email_controller



# run 	sudo service redis-server start
import redis.exceptions
from lambda_layer.rainforest_api import search_amazon_products
from lambda_layer.ebay_api import search_ebay_products
app = Flask(__name__)
# Allow CORS from frontend dev server
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# Configure Redis
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    password=os.getenv('REDIS_PASSWORD', None),
    db=0
)

setup_indexes()

@app.route("/api/hello")
def api_hello():
    return {"message": "Hello from Python backend"}

@app.route("/api/search")
def api_search():
    search_term = request.args.get("search")
    if not search_term:
        return {"error": "Missing search term"}, 400
    try:
        cache_key = f"search:{search_term}"
        cached_results = redis_client.get(cache_key)

        if cached_results:
            return jsonify(json.loads(cached_results.decode('utf-8')))
    except redis.exceptions.ConnectionError:
        pass

    try:
       # amazon_results = search_amazon_products(search_term)
        ebay_results = search_ebay_products(search_term)

        combined_results = {
          # 'amazon': amazon_results,
            'ebay': ebay_results
        }
        try:
            redis_client.setex(cache_key, timedelta(hours=1), json.dumps(combined_results))
        except redis.exceptions.ConnectionError:
            pass
        return jsonify(combined_results)
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/api/signup", methods=["POST"])
def api_create_user():
    return signup_user_controller()

@app.route("/api/users/<user_id>", methods=["PATCH"])
def api_edit_user(user_id):
    return edit_user_controller(user_id)

@app.route("/api/verifyEmail", methods=["POST"])
def api_verify_signup():
    return verify_signup_code_controller()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
