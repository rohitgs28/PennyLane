from __future__ import annotations
from app.extensions import db, migrate
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Any, Dict, Optional

from app.extensions import db, migrate
from app.graphql.schema import schema  
from app.models import Challenge  
from app.graphql.schema import schema
from app.cli import register_cli
from app.routes.main import api as api_bp


def create_app(config_override: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Application factory.

    Args:
        config_override: Optional dict of config values to apply after loading default config.
                         Tests can pass {"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"} etc.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object("config")

    # Allow tests or env-specific callers to override config safely.
    if config_override:
        app.config.update(config_override)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # --- CORS ---
    # Explicitly allow the Authorization header so browsers can send it cross-origin.
    CORS(
        app,
        resources={
            r"/graphql": {"origins": "http://localhost:3000"},
            r"/api/*": {"origins": "http://localhost:3000"},
        },
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
    )

    # CLI
    register_cli(app)

    # Register blueprints (REST)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/", methods=["GET"])
    def health_check() -> Any:
        """Simple health check used by tests and monitoring."""
        return "PennyLane Support API is up!", 200

    # Single GraphQL endpoint (POST). We intentionally avoid flask-graphql (deprecated).
    @app.route("/graphql", methods=["POST", "OPTIONS"])
    def graphql_server() -> Any:
        """
        GraphQL endpoint.

        Accepts JSON body with fields:
            - query: GraphQL query string
            - variables: optional dict of variables
            - operationName: optional operation name

        Returns:
            JSON response with optional "data" and/or "errors".
        """
        if request.method == "OPTIONS":
            return "", 200  # CORS preflight

        data = request.get_json(silent=True) or {}
        query = data.get("query")
        variables = data.get("variables")
        operation_name = data.get("operationName")

        result = schema.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            context_value={"session": db.session, "request": request},
        )

        payload: Dict[str, Any] = {}
        if result.errors:
            payload["errors"] = [str(e) for e in result.errors]
        if result.data:
            payload["data"] = result.data
        return jsonify(payload), 200

    return app
