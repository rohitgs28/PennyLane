# app/__init__.py
from __future__ import annotations

from typing import Any, Dict, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS

from app.extensions import db, migrate
from app.graphql.schema import schema
from app.cli import register_cli
from app.routes.main import api as api_bp


def create_app(config_override: Optional[Dict[str, Any]] = None) -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object("config")

    # Allow tests / env-specific callers
    if config_override:
        app.config.update(config_override)

    # --------------------------------------------------------------------- #
    #  Extensions
    # --------------------------------------------------------------------- #
    db.init_app(app)
    migrate.init_app(app, db)

    # --------------------------------------------------------------------- #
    #  CORS – allow React dev server to reach /graphql and /api/*
    # --------------------------------------------------------------------- #
    CORS(
        app,
        resources={
            r"/graphql": {"origins": ["http://localhost:3000"]},
            r"/api/*":   {"origins": ["http://localhost:3000"]},
        },
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type"],
        max_age=86400,          # cache pre-flight for a day
        send_wildcard=False,    # return the exact origin, not '*'
        always_send=True,       # send CORS headers on 4xx/5xx too
    )

    # --------------------------------------------------------------------- #
    #  CLI and blueprints
    # --------------------------------------------------------------------- #
    register_cli(app)
    app.register_blueprint(api_bp, url_prefix="/api")

    # --------------------------------------------------------------------- #
    #  Routes
    # --------------------------------------------------------------------- #
    @app.route("/", methods=["GET"])
    def health_check() -> Any:
        return "PennyLane Support API is up!", 200

    @app.route("/graphql", methods=["POST", "OPTIONS"])
    def graphql_server() -> Any:
        # CORS pre-flight is handled automatically by flask-cors,
        # but browsers still send an OPTIONS; we simply 200 it.
        #if request.method == "OPTIONS":
         #   return "", 200

        data = request.get_json(silent=True) or {}
        result = schema.execute(
            data.get("query"),
            variable_values=data.get("variables"),
            operation_name=data.get("operationName"),
            context_value={"session": db.session, "request": request},
        )

        payload: Dict[str, Any] = {}
        if result.errors:
            payload["errors"] = [str(err) for err in result.errors]
        if result.data:
            payload["data"] = result.data
        return jsonify(payload), 200

    # --------------------------------------------------------------------- #
    return app
