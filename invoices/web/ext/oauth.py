import base64
import json
from flask import current_app, session, request
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
        app.config.setdefault("OAUTH_REDIRECT_URI", None)
        app.config.setdefault("OAUTH_SCOPE", "openid email")

    def get_authorization_url(self):
        sess = OAuth2Session(
            self.app.config["OAUTH_CLIENT_ID"],
            redirect_uri=self.app.config["OAUTH_REDIRECT_URI"],
            scope=self.app.config["OAUTH_SCOPE"],
        )
        authorization_url, state = sess.authorization_url(
            self.app.config["OAUTH_AUTHORIZATION_BASE_URL"]
        )
        session["OAUTH_STATE"] = state
        return authorization_url

    def fetch_user(self):
        sess = OAuth2Session(
            self.app.config["OAUTH_CLIENT_ID"],
            state=session["OAUTH_STATE"],
            redirect_uri=self.app.config["OAUTH_REDIRECT_URI"],
        )
        token = sess.fetch_token(
            self.app.config["OAUTH_TOKEN_URL"],
            client_secret=self.app.config["OAUTH_CLIENT_SECRET"],
            authorization_response=request.url,
        )
        id_token = token["id_token"]
        return self._decode_user_from_id_token(id_token)

    def _decode_user_from_id_token(self, id_token):
        _, payload_raw, _ = id_token.split(".")
        missing_padding = len(payload_raw) % 4
        payload_raw_decoded = base64.b64decode(payload_raw + "=" * missing_padding)
        payload = json.loads(payload_raw_decoded)
        return payload
