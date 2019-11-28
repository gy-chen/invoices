
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from invoices.oauth.web.ext import oauth_ext
from invoices.user.web.ext import user_model_ext
from invoices.user_invoice.web.ext import user_invoice_model_ext
from invoices.sqlalchemy import Base


db = SQLAlchemy(model_class=Base)
migrate = Migrate(db=db)


def create_app(config):
    from invoices.login.web.blueprint import bp as bp_login
    from invoices.user_invoice.web.blueprint import bp as bp_user_invoices
    from invoices.qrcode.bp import bp as bp_qrcode

    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app)
    oauth_ext.init_app(app)
    user_model_ext.init_app(app, db.session)
    user_invoice_model_ext.init_app(app, db.session)

    app.register_blueprint(bp_login)
    app.register_blueprint(bp_user_invoices)
    app.register_blueprint(bp_qrcode, url_prefix="/qrcode")

    return app

