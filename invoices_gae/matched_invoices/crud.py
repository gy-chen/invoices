#coding: utf-8
import six
from flask import Blueprint, request, render_template, redirect, url_for, current_app, Response
from .. import invoices
from . import model, helper
from ..auth import oauth2

crud = Blueprint('matched_invoices', __name__, template_folder='templates')

@crud.route('/')
@oauth2.required
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    user_id = invoices.model.InvoiceModel.get_login_user_id()
    matched_invoices, next_page_token = invoices.model.Invoice.list_matched(user_id, cursor=token)

    # register filters
    current_app.jinja_env.filters['readable_month'] = helper.readable_month
    return render_template(
        'matched_invoices/list.html',
        matched_invoices=matched_invoices,
        next_page_token=next_page_token)

@crud.route('/tasks/match_invoices')
def test():
    model.MatchInvoiceModel.match_invoices()
    return Response(status=200)
