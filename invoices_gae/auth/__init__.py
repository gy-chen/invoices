#coding: utf-8
from flask import Blueprint, request, redirect
from oauth2client.contrib.flask_util import UserOAuth2
from six.moves import urllib
from .authmanager import AuthManager

DEFAULT_JWT_RETURN_URL = 'gychen_invoices://login_jwt'

auth_manager = AuthManager()
oauth2 = UserOAuth2()
oauth2.authorize_callback = auth_manager.login_callback

def register_blueprint(app, url_prefix=""):
    """Register auth functions to the app.

    """
    oauth2.init_app(
        app,
        scopes=['email', 'profile'])
    # XXX workaround for init_app overwriting authorize_callback problem
    oauth2.authorize_callback = auth_manager.login_callback

    auth_blueprint = Blueprint('auth', __name__)

    @auth_blueprint.route('/login_jwt', defaults={'return_url': DEFAULT_JWT_RETURN_URL})
    @auth_blueprint.route('/login_jwt/<return_url>')
    @oauth2.required
    def login_jwt(return_url):
        # get the credentials and put credentials as jwt
        encoded = auth_manager.get_login_jwt()
        # redirect to return url with jwt
        return_url_parsed = urllib.parse.urlparse(return_url)
        qs_dict = urllib.parse.parse_qs(return_url_parsed.query)
        qs_dict['jwt'] = encoded
        qs_str = urllib.parse.urlencode(qs_dict)
        final_return_url = urllib.parse.urljoin(return_url, '?' + qs_str)
        return redirect(final_return_url)

    @auth_blueprint.route('/logout')
    def logout():
        auth_manager.logout()
        return redirect(request.referrer or '/')

    app.register_blueprint(auth_blueprint, url_prefix=url_prefix)
