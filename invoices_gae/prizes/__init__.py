#coding: utf-8

from .crud import crud

def register_blueprint(app, url_prefix):
    app.register_blueprint(crud, url_prefix=url_prefix)
