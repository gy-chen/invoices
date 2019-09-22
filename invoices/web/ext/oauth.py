from flask import current_app, sesion, request
from requests_oauthlib import OAuth2Session


class OAuth:
    def __init__(self, app=None):
        self._app = app

    @property
    def app(self):
        if self._app:
            return self._app
        return current_app

    def init_app(self, app):
        app.config.setdefault("OAUTH_CLIENT_ID", None)
        app.config.setdefault("OAUTH_CLIENT_SECRET", None)
        app.config.setdefault("OAUTH_AUTHORIZATION_BASE_URL", None)
        app.config.setdefault("OAUTH_TOKEN_URL", None)
        app.config.setdefault("OAUTH_USER_PROFILE_URL", None)

    def get_authorization_url(self):
        session = OAuth2Session(app.config["OAUTH_CLIENT_ID"])
        authorization_url, state = session.authorization_url(
            app.config["OAUTH_AUTHORIZATION_BASE_URL"]
        )
        session["OAUTH_STATE"] = state
        return authorization_url

    def fetch_user(self):
        session = OAuth2Session(
            app.config["OAUTH_CLIENT_ID"], state=session["OAUTH_STATE"]
        )
        token = session.fetch_token(
            app.config["OAUTH_TOKEN_URL"],
            client_secret=app.config["OAUTH_CLIENT_SECRET"],
            authorization_response=request.url,
        )
        user = session.get(app.config["OAUTH_USER_PROFILE_URL"]).json()
        return user
