from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from invoices.web.ext.oauth import OAuth
from invoices.model import Base, UserModel, InvoiceModel, UserInvoiceModel

oauth = OAuth()
db = SQLAlchemy(model_class=Base)
user_model = UserModel(db.session)
invoice_model = InvoiceModel(db.session)
user_invoice_model = UserInvoiceModel(db.session)


def create_app(config):
    from invoices.web.login import bp as bp_login

    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    oauth.init_app(app)

    app.register_blueprint(bp_login)

    return app

