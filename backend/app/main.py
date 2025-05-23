import os
import json
from datetime import timedelta

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


from app.db.mongo_client import db
from app.db.indexes import setup_indexes
from app.controllers.userController import (
    signup_user_controller,
    edit_user_controller,
    verify_code_controller,
    login_user_controller
)
from app.controllers.searchController import search_products_controller

app = Flask(__name__)
# Allow CORS from frontend dev server
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})



# Initialize limiter with default rate limit per IP
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

setup_indexes()

@app.route("/api/search")
def api_search():
    return search_products_controller()
@app.route("/api/signup", methods=["POST"])
# @limiter.limit("5 per 10 minutes")
def api_create_user():
    return signup_user_controller()

@app.route("/api/users/<user_id>", methods=["PATCH"])
# @limiter.limit("10 per hour")
def api_edit_user(user_id):
    return edit_user_controller(user_id)

@app.route("/api/verifyEmail", methods=["POST"])
# @limiter.limit("5 per 10 minutes")
def api_verify_signup():
    return verify_code_controller()

@app.route("/api/login", methods=["POST"])
# @limiter.limit("5 per 10 minutes") 
def api_login_user():
    return login_user_controller()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
