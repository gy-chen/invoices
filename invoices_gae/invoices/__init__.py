#coding: utf-8

from .crud import crud
from .api import api

def register_blueprint(app, url_prefix):
    app.register_blueprint(crud, url_prefix=url_prefix)
    app.register_blueprint(api, url_prefix=url_prefix)
