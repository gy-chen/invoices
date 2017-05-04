import logging
from flask import current_app, Flask, redirect, url_for

def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(config)

    app.debug = debug
    app.testing = testing

    if config_overrides:
        app.config.update(config_overrides)

    # Configure logging
    if not app.testing:
        logging.basicConfig(level=logging.INFO)

    from . import auth
    auth.register_blueprint(app)
    from . import base
    base.register_blueprint(app)
    from . import invoices
    invoices.register_blueprint(app, url_prefix='/invoices')
    from . import prizes
    prizes.register_blueprint(app, url_prefix='/prizes')
    from . import matched_invoices
    matched_invoices.register_blueprint(app, url_prefix='/matched_invoices')

    @app.route('/')
    @auth.oauth2.required
    def index():
        return redirect(url_for('crud.list'))

    return app
