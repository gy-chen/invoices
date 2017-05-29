#coding: utf-8
from flask import Blueprint, request, redirect
from oauth2client.contrib.flask_util import UserOAuth2
from six.moves import urllib
from .authmanager import AuthManager

DEFAULT_JWT_RETURN_URL = 'gychen_invoices://login_jwt'

oauth2 = UserOAuth2()

def get_auth_manager_instance(oauth2=None):
    instance = getattr(get_auth_manager_instance, '_instance', None)
    if instance:
        return instance
    if oauth2 is None:
        raise ValueError("Plase provide oauth2 argument.")
    setattr(get_auth_manager_instance, '_instance', AuthManager(oauth2))
    return get_auth_manager_instance()


def register_blueprint(app, url_prefix=""):
    """Register auth functions to the app.

    """
    oauth2.init_app(
        app,
        scopes=['email', 'profile'])
    auth_manager = get_auth_manager_instance(oauth2)

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
