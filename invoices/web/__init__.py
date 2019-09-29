from flask import Flask
from invoices.web.ext.oauth import OAuth

oauth = OAuth()
# TODO setup sqlalchemy and model class
user_model = None


def create_app(config):
    from invoices.web.login import bp as bp_login

    app = Flask(__name__)
    app.config.from_object(config)

    oauth.init_app(app)

    app.register_blueprint(bp_login)

    return app

