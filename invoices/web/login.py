import functools
import jwt
from flask import Blueprint, redirect, jsonify, current_app, request, g, abort
from werkzeug.local import LocalProxy
from invoices.web import oauth, db, user_model
from invoices.model import User

bp = Blueprint("login", __name__)


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
        user = _load_user(token_data["sub"])
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


def _load_user(sub):
    return user_model.get_user(sub)


def get_current_user():
    if "current_user" not in g:
        g.current_user = get_user_from_request()
    return g.current_user


current_user = LocalProxy(get_current_user)


def required_login(f):
    @functools.wraps(f)
    def wrapper(*args, **kargs):
        current_user = get_current_user()
        if current_user is None:
            abort(403)
        return f(*args, **kargs)

    return wrapper


@bp.route("/login")
def login():
    """Start point for login

    1. generate state and authorization url
    2. save state to session
    3. redirect to authorization url
    """
    authorization_url = oauth.get_authorization_url()
    return redirect(authorization_url)


@bp.route("/login_callback")
def login_callback():
    """OAuth callback

    1. retrieve code from request
    2. exchange access token
    3. fetch user profile
    4. generate JWT token for the user
    5. return JWT token
    """
    profile = oauth.fetch_user()
    user = User(profile["sub"], profile["email"])
    user_model.register_user(user)
    token = login_user(user)
    db.session.commit()
    return jsonify(token=token)
