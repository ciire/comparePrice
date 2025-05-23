from flask import request, jsonify
from app.services.search_service import search_results

def search_products_controller():
    search_term = request.args.get("search")
    if not search_term:
        return {"error": "Missing search term"}, 400

    try:
        results = search_results(search_term)
        return jsonify(results)
    except Exception as e:
        return {"error": str(e)}, 500
