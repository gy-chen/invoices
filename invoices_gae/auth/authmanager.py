#coding: utf-8
import jwt
import httplib2
import json
import oauth2client.client
from flask import session


# XXX maybe use this class as singleton, not as a class that can
# be instance. Put dependency to oauth2 to other place.
class AuthManager:
    JWT_SECRET = b'p\xbb+\xcfU\x06\xaf\x8e\xb6P60\x14\x88t(W\xfb:L\x82+\x0e\xa1\xc2\x11g`\xdf\xb3\xc0q'
    JWT_PARAM_KEY_CREDENTIALS = 'payload'
    SESSION_KEY_JWT = 'login_jwt'
    SESSION_KEY_PROFILE = 'profile'

    def get_login_user(self):
        """Get current login user

        return None if user is not login.
        """
        return session.get(self.SESSION_KEY_PROFILE, None)

    def get_login_user_by_jwt(self, jwt_):
        """Get current login user by jwt token.

        This function will use credentials that stored in jwt to fetch profile
        of login user.
        Return None if user is not login.
        """
        try:
            credentials_s = jwt.decode(jwt_, key=self.JWT_SECRET, algorithms=['HS256'])[self.JWT_PARAM_KEY_CREDENTIALS]
        except jwt.exceptions.DecodeError:
            return None
        credentials = oauth2client.client.Credentials.new_from_json(credentials_s)
        return self._fetch_google_profile(credentials)

    def login_callback(self, credentials):
        """Callback function of OAuth2
        """
        profile = self._fetch_google_profile(credentials)
        if profile is None:
            return False
        # generate jwt that containes credentials
        encoded = jwt.encode({self.JWT_PARAM_KEY_CREDENTIALS: credentials.to_json()}, self.JWT_SECRET, algorithm='HS256')
        # Save jwt in session to prevent other user fetch it
        # Flask store data in cookie, not in server size. So store jwt in
        # session will exceed max data limit of cookie.
        # Must use Flas-Session to store session in service-side to make this
        # function works.
        session[self.SESSION_KEY_JWT] = encoded
        session[self.SESSION_KEY_PROFILE] = profile

    def _fetch_google_profile(self, credentials):
        """Fetch Google Plus Profile by Google API.

        return dict that contains profile information, or return None if fetch failed.
        """
        http = httplib2.Http()
        credentials.authorize(http)
        resp, content = http.request(
            'https://www.googleapis.com/plus/v1/people/me')
        if resp.status != 200:
            return None
        return json.loads(content.decode('utf-8'))

    def get_login_jwt(self):
        """Get the previous generated jwt
        """
        return session.get(self.SESSION_KEY_JWT, None)

    def logout(self):
        if self.SESSION_KEY_PROFILE in session:
            del session[self.SESSION_KEY_PROFILE]
