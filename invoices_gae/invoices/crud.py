#coding: utf-8`
import six
from flask import Blueprint, request, render_template, redirect, url_for, current_app
from . import model, helper
from ..auth import oauth2

crud = Blueprint('crud', __name__, template_folder='templates')

@crud.route('/')
@oauth2.required
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    user_id = model.InvoiceModel.get_login_user_id()
    invoices, next_page_token = model.Invoice.list_of_user(user_id, cursor=token)

    # register filters
    current_app.jinja_env.filters['readable_month'] = helper.readable_month
    current_app.jinja_env.filters['readable_matched_prize_id'] = helper.readable_matched_prize_id
    return render_template(
        'invoices/list.html',
        invoices=invoices,
        next_page_token=next_page_token)

@crud.route('/add', methods=['GET', 'POST'])
@oauth2.required
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        try:
            invoice_data = model.InvoiceModel.for_add(data)
            invoice = model.Invoice.create(invoice_data)
        except model.InvalidInvoiceException as e:
            errors = e.args
            return render_template('form.html', action='Add', invoice=data, errors=errors)

        return redirect(url_for('.add', message=helper.MESSAGE_SUCCESSFUL))

    message = request.args.get('message', 0)
    messages = helper.get_messages_for_add(message)

    return render_template('invoices/form.html', action='Add', invoice=None, messages=messages)

@crud.route('/<id>/edit', methods=['GET', 'POST'])
@oauth2.required
def edit(id):
    invoice = model.Invoice.read(id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        try:
            invoice_data = model.InvoiceModel.for_update(data, id)
            invoice = model.Invoice.update(invoice_data, id)
        except model.InvalidInvoiceException as e:
            errors = e.args
            return render_template('form.html', action='Update', invoice=data, errors=errors)

        return redirect(url_for('.view', id=invoice.key.id))

    return render_template('invoices/form.html', action="Edit", invoice=invoice)

@crud.route('/<id>')
@oauth2.required
def view(id):
    invoice = model.Invoice.read(id)

    return render_template('invoices/view.html', invoice=invoice)

@crud.route('/<id>/delete')
@oauth2.required
def delete(id):
    model.Invoice.delete(id)
    return redirect(url_for('.list'))
