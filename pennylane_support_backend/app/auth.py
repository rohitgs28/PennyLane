from __future__ import annotations

import json
import os
import ssl
from functools import wraps
from typing import Any, Dict, List, Optional

from flask import g, request
from urllib.error import URLError
from urllib.request import urlopen

# Use python-jose for JWT handling
from jose import jwt, JWTError, ExpiredSignatureError


AUTH0_DOMAIN: str = os.getenv("AUTH0_DOMAIN", "")
API_IDENTIFIER: str = os.getenv("API_IDENTIFIER", "")
ALGORITHMS: List[str] = os.getenv("ALGORITHMS", "RS256").split(",")
NAMESPACE: str = os.getenv("AUTH0_NAMESPACE", "https://pennylane.app/")
SKIP_TLS: bool = os.getenv("FLASK_SKIP_TLS_VERIFY") == "1"


def _download_json(url: str) -> Dict[str, Any]:
    def _open(ctx: Optional[ssl.SSLContext]) -> bytes:
        return urlopen(url, context=ctx).read()

    try:
        # If SKIP_TLS is set, use an unverified context (for dev only!)
        if SKIP_TLS:
            ctx = ssl._create_unverified_context()  # type: ignore[attr-defined]
            return json.loads(_open(ctx))
        # Try with the default context first
        return json.loads(_open(None))
    except URLError as err:
        # On macOS the default CA bundle might be missing; retry with certifi
        if isinstance(getattr(err, "reason", None), ssl.SSLCertVerificationError):
            try:
                import certifi
                ctx = ssl.create_default_context(cafile=certifi.where())
                return json.loads(_open(ctx))
            except Exception:
                pass
        # Re-raise if we cannot recover
        raise


class AuthError(Exception):
    """Standardised error raised on authentication/authorization failures."""
    def __init__(self, error: Dict[str, str], status_code: int) -> None:
        super().__init__(error)
        self.error = error
        self.status_code = status_code


def _extract_bearer(header_value: Optional[str]) -> Optional[str]:
    if not header_value:
        return None
    parts = header_value.split()
    if parts[0].lower() == "bearer" and len(parts) == 2:
        return parts[1]
    return None

def get_token_auth_header() -> str:
    """Return the JWT from the Authorization header, an alternate header,
    or from a cookie.  Raises AuthError if no token can be found."""
    # 1) Standard Authorization header
    token = _extract_bearer(request.headers.get("Authorization"))
    if token:
        return token

    # 2) Alternate header names (belt & suspenders)
    alt = request.headers.get("X-Access-Token") or request.headers.get("x-access-token")
    if alt and alt.strip():
        return alt.strip()

    # 3) Common cookie names (if tokens are stored in cookies)
    for name in ("access_token", "accessToken", "access-token"):
        cookie_val = request.cookies.get(name)
        if cookie_val:
            return cookie_val

    # If nothing is found, raise an error
    raise AuthError(
        {"code": "authorization_header_missing",
         "description": "Authorization header expected"},
        401,
    )


def requires_auth(_fn=None, *, required_role: Optional[str] = None):
    """
    Decorator to enforce JWT authentication (and optional role gating).
    Usage:
      @requires_auth                      → any authenticated user
      @requires_auth(required_role="support_admin") → only users with that role
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Fetch the bearer token
            token = get_token_auth_header()

            # Fetch JWKS with robust SSL handling
            jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
            jwks = _download_json(jwks_url)

            # Validate token header and find matching JWK
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            if not kid:
                raise AuthError(
                    {"code": "invalid_header",
                     "description": "Invalid token header."},
                    401,
                )
            rsa_key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
            if not rsa_key:
                raise AuthError(
                    {"code": "invalid_header",
                     "description": "Unable to find matching JWKS key."},
                    401,
                )

            # Validate and decode the JWT using python-jose
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_IDENTIFIER,
                    issuer=f"https://{AUTH0_DOMAIN}/",
                )
            except ExpiredSignatureError:
                raise AuthError(
                    {"code": "token_expired",
                     "description": "Token expired."},
                    401,
                )
            except JWTError as e:
                # All other JWT errors (invalid claims, bad signature, etc.)
                raise AuthError(
                    {"code": "invalid_header",
                     "description": str(e)},
                    401,
                )

            ns = (NAMESPACE or "https://pennylane.app/").rstrip("/") + "/" 
            g.current_user = {                                        
                "sub": payload.get("sub"),
                "email": payload.get(f"{ns}email") or payload.get("email"),
                "name":  payload.get(f"{ns}name")  or payload.get("name"),
                "nickname": payload.get("nickname"),
            }
            g.roles = payload.get(f"{ns}roles", []) 

            # If a role is required, verify it
            if required_role and required_role not in g.roles:
                raise AuthError(
                    {"code": "forbidden",
                     "description": f"Role '{required_role}' required."},
                    403,
                )

            # Call the wrapped function
            return func(*args, **kwargs)

        return wrapper

    # Support both @requires_auth and @requires_auth(...)
    if callable(_fn):
        return decorator(_fn)
    return decorator
