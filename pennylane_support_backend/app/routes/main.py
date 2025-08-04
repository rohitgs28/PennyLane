from __future__ import annotations

from flask import Blueprint, jsonify
from app.auth import requires_auth

# This blueprint contains REST-style endpoints under /api/*
api = Blueprint("api", __name__)

@api.route("/secure-data", methods=["GET"])
@requires_auth
def secure_data():
    """
    Example protected endpoint.

    Returns:
        JSON payload when the caller is authenticated by @requires_auth.
    """
    return jsonify(message="This is a protected route.")
