from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
import os
from routes import init_routes

from models import setup_db

def create_app(test_config=None):

    # create and configure the app
    load_dotenv()
    app = Flask(__name__)
    itemsBatchSize = 10
    if os.getenv("ITEMS_BATCH_SIZE") is not None:
        itemsBatchSize = 10
    app.config["ITEMS_BATCH_SIZE"] = itemsBatchSize
    if test_config is None:
        setup_db(app, os.getenv("DATABASE_PATH"))
    elif test_config == "test":
        setup_db(app, os.getenv("TEST_DATABASE_PATH"))

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods",
            "GET,PATCH,POST,DELETE,OPTIONS"
        )
        return response

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "msg": "bad request, please check your input params...",
            "success": False,
            "data": None
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "msg": "resource not found, aborting...",
            "success": False,
            "data": None
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "msg": "could not process your request, aborting...",
            "success": False,
            "data": None
        }), 422

    @app.errorhandler(500)
    def unprocessable(error):
        return jsonify({
            "msg": "server error, please try again later...",
            "success": False,
            "data": None
        }), 500

    init_routes(app)

    return app
