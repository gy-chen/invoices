from flask import Blueprint
from flask import redirect
from flask import jsonify
from flask import current_app
from flask import request
from flask import session
from werkzeug.urls import Href
from invoices.oauth.web.ext import oauth_ext
from invoices.user.web.ext import user_model_ext
from invoices.login.web import is_valid_callback_url
from invoices.login.web import login_user

bp = Blueprint("login", __name__)


@bp.route("/login")
def login():
    """Start point for login

    1. generate state and authorization url
    2. save state to session
    3. redirect to authorization url
    """
    authorization_url = oauth_ext.get_authorization_url()
    callback_url = request.args.get("callback_url")
    if is_valid_callback_url(callback_url):
        session["callback_url"] = callback_url
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
    profile = oauth_ext.fetch_user()
    user = user_model_ext.user_model.register_user(profile["sub"], profile["email"])
    token = login_user(user)

    callback_url = session.get("callback_url")
    if callback_url:
        return redirect(Href(callback_url)(token=token))
    return jsonify(token=token)
