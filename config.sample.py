SECRET_KEY = 'your flask secret key'

OAUTH_CLIENT_ID = (
    "your oauth client id"
)

OAUTH_CLIENT_SECRET = "your oauth client secret"
OAUTH_AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
OAUTH_REDIRECT_URI = "http://127.0.0.1:5000/login_callback"
OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
OAUTH_SCOPE = "openid email"

LOGIN_JWT_SECRET = "your login jwt secret"

SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

LOGIN_VALID_CALLBACK_URLS = ['http://127.0.0.1:5000']