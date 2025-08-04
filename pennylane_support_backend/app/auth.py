import json
from functools import wraps
from urllib.request import urlopen
from flask import request, g
from jose import jwt, JWTError
import os

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_IDENTIFIER = os.getenv("API_IDENTIFIER")
AUTH0_NAMESPACE = os.getenv("AUTH0_NAMESPACE", "https://pennylane.app/")
ALGORITHMS = [os.getenv("ALGORITHMS", "RS256")]

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def _extract_bearer(header_value: str | None):
    if not header_value:
        return None
    parts = header_value.split()
    if parts[0].lower() == "bearer" and len(parts) == 2:
        return parts[1]
    return None

def get_token_auth_header():
    # 1) Authorization: Bearer
    token = _extract_bearer(request.headers.get("Authorization"))
    if token:
        return token

    # 2) Alternate header (belt & suspenders)
    alt = request.headers.get("X-Access-Token") or request.headers.get("x-access-token")
    if alt and alt.strip():
        return alt.strip()

    # 3) Common cookie names (if you choose to set them)
    for name in ("access_token", "accessToken", "access-token"):
        cookie_val = request.cookies.get(name)
        if cookie_val:
            return cookie_val

    raise AuthError(
        {"code": "authorization_header_missing", "description": "Authorization header expected"},
        401,
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        try:
            jwks = json.loads(urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json").read())
            unverified_header = jwt.get_unverified_header(token)
        except Exception:
            raise AuthError({"code": "invalid_header", "description": "Invalid token header."}, 401)

        if "kid" not in unverified_header:
            raise AuthError({"code": "invalid_header", "description": "Token is not a valid RS256 JWT (kid missing)."}, 401)

        rsa_key = next(
            (
                {
                    "kty": k["kty"],
                    "kid": k["kid"],
                    "use": k["use"],
                    "n": k["n"],
                    "e": k["e"],
                }
                for k in jwks["keys"]
                if k["kid"] == unverified_header["kid"]
            ),
            None,
        )
        if not rsa_key:
            raise AuthError({"code": "invalid_header", "description": "Unable to find matching JWKS key."}, 401)

        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_IDENTIFIER,
                issuer=f"https://{AUTH0_DOMAIN}/",
            )
        except jwt.ExpiredSignatureError:
            raise AuthError({"code": "token_expired", "description": "Token expired."}, 401)
        except JWTError as e:
            raise AuthError({"code": "invalid_claims", "description": str(e)}, 401)

        g.current_user = payload
        g.roles = payload.get(f"{AUTH0_NAMESPACE}roles", [])
        return f(*args, **kwargs)
    return decorated
