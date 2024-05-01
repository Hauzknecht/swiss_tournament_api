from datetime import timedelta
from flask import Flask, jsonify
import os
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS

from db import db
from blocklist import BLOCKLIST

from resources.user import blp as UserBlueprint
from resources.tournament import blp as TournamentBluePrint


def create_app(db_url=None):
    app = Flask(__name__)
    CORS(app)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True 
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate = Migrate(app, db)

    api = Api(app)

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET", "80356663116568293133861074020168941030")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=1)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_hedaer, jwt_paylaod):
        return(
            jsonify({"description": "Token has been revoked.", "error": "token_revoked"}),
            401,
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": "True"}
        return {"is_admin": "False"}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "the token has expired.", "error": "token_expired"}),
            401,
        )
    
    @jwt.invalid_token_loader
    def invlaid_token_callback(error):
        return (
            jsonify({"message": "Signature verification failed.", "error": "invalid_token"}),
            401,
        )
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify({"description": "Request does not contain an access token.", "error": "authorization_required"}),
            401,
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify({"description": "The token is not fresh.", "error": "fresh_token_required"}),
            401,
        )
    
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(TournamentBluePrint)

    return app