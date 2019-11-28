import functools
import jwt
from flask import abort
from flask import current_app
from flask import request
from flask import g
from werkzeug.local import LocalProxy
from invoices.user.web.ext import user_model_ext


def login_user(user):
    """Login user

    Generate and return JWT token for user identity

    Args:
        user

    Returns:
        str: jwt token
    """
    secret = current_app.config["LOGIN_JWT_SECRET"]
    token = jwt.encode({"sub": user.sub}, secret, algorithm="HS256")
    return token.decode()


def get_user_from_request():
    """Try to get user from request

    1. try to fetch JWT token from request
    2. try to load user from identity retrieved from JWT token

    Returns:
        user or None
    """
    token = _get_token_from_request()
    if not token:
        return None
    try:
        token_data = jwt.decode(
            token, current_app.config["LOGIN_JWT_SECRET"], algorithm="HS256"
        )
        user = user_model_ext.user_model.load_user(token_data["sub"])
        if user is None:
            current_app.logger.warn(
                "jwt token is valid, but user is not found: %s", token_data["sub"]
            )
        return user
    except jwt.InvalidTokenError as e:
        current_app.logger.info("failed to login: %s", e)
        return None


def _get_token_from_request():
    auth_header = request.headers.get("Authorization", None)
    if not auth_header:
        return None
    try:
        _, token = auth_header.split()
        return token
    except ValueError:
        return None


def _get_current_user():
    if "current_user" not in g:
        g.current_user = get_user_from_request()
    return g.current_user


current_user = LocalProxy(_get_current_user)


def required_login(f):
    @functools.wraps(f)
    def wrapper(*args, **kargs):
        current_user = _get_current_user()
        if current_user is None:
            abort(403)
        return f(*args, **kargs)

    return wrapper


def is_valid_callback_url(callback_url):
    for valid_callback_url in current_app.config["LOGIN_VALID_CALLBACK_URLS"]:
        if callback_url.startswith(valid_callback_url):
            return True
    return False
