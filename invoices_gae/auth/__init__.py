#coding: utf-8
from flask import Blueprint, request, redirect
from oauth2client.contrib.flask_util import UserOAuth2
from .authmanager import AuthManager

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

    @auth_blueprint.route('/logout')
    def logout():
        auth_manager.logout()
        return redirect(request.referrer or '/')

    app.register_blueprint(auth_blueprint, url_prefix=url_prefix)
