#coding: utf-8
from flask import Blueprint

base_templates = Blueprint('base_templates', __name__, template_folder='templates')

def register_blueprint(app):
    app.register_blueprint(base_templates)
