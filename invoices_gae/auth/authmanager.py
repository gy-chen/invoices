#coding: utf-8
import httplib2
import json
from flask import session


class AuthManager:

    SESSION_KEY_PROFILE = 'profile'

    def __init__(self, oauth2):
        oauth2.authorize_callback = self.login
        self.oauth2 = oauth2
        self._instance = self

    def get_login_user(self):
        """Get current login user

        return None if user is not login.
        """
        return session.get(self.SESSION_KEY_PROFILE, None)

    def login(self, credentials):
        http = httplib2.Http()
        credentials.authorize(http)
        resp, content = http.request(
            'https://www.googleapis.com/plus/v1/people/me')

        if resp.status != 200:
            return False
        session[self.SESSION_KEY_PROFILE] = json.loads(content.decode('utf-8'))
        return True

    def logout(self):
        self.oauth2.storage.delete()
        if self.SESSION_KEY_PROFILE in session:
            del session[self.SESSION_KEY_PROFILE]
