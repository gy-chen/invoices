from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from invoices.web.ext.oauth import OAuth
from invoices.model import (
    Base,
    UserModel,
    InvoiceModel,
    UserInvoiceModel,
    UserInvoiceMatchModel,
)

oauth = OAuth()
db = SQLAlchemy(model_class=Base)
migrate = Migrate(db=db)
user_model = UserModel(db.session)
invoice_model = InvoiceModel(db.session)
user_invoice_model = UserInvoiceModel(db.session)
user_invoice_match_model = UserInvoiceMatchModel(db.session)


def create_app(config):
    from invoices.web.login import bp as bp_login
    from invoices.web.user_invoices import bp as bp_user_invoices
    from invoices.qrcode.bp import bp as bp_qrcode

    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app)
    oauth.init_app(app)

    app.register_blueprint(bp_login)
    app.register_blueprint(bp_user_invoices)
    app.register_blueprint(bp_qrcode, url_prefix="/qrcode")

    return app

