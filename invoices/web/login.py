from flask import Blueprint, redirect, jsonify
from invoices.web import oauth

bp = Blueprint("login", __name__)


def login_user(user):
    """Login user

    Generate and return JWT token for user identity

    Args:
        user

    Returns:
        str: jwt token
    """
    pass


def get_user_from_request():
    """Try to get user from request

    1. try to fetch JWT token from request
    2. try to load user from identity retrieved from JWT token

    Returns:
        user or None
    """
    pass


def load_user(sub):
    pass


def get_current_user():
    pass


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
    user = oauth.fetch_user()
    token = login_user(user)
    return jsonify(token=token)