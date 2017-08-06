#coding: utf-8
from flask import abort, Blueprint, request, jsonify
from . import model

api = Blueprint('api_invoices', __name__)

def validate_jwt():
    """Validate user passing a correct jwt.

    This function will decode jwt and use it as credentials in Google OAuth2.

    abort if the jwt is not correct or credentials has problem.

    return login user id if successful
    """
    jwt = request.args.get('jwt')
    login_user_id = model.InvoiceApiModel.validate_login_jwt(jwt)
    if not login_user_id:
        abort(403)

api.before_request = validate_jwt

@api.route('/api/list')
def list():
    login_user_id = model.InvoiceApiModel.get_login_user_id()
    token = request.args.get('token')
    # list all invoices
    invoices, next_page_token = model.Invoice.list_of_user(login_user_id, cursor=token)
    return jsonify(invoices=invoices, token=next_page_token)

@api.route('/api/add', methods=['POST'])
def add():
    data = request.form.to_dict(flat=True)
    try:
        invoice_data = model.InvoiceApiModel.for_add(data)
        invoice = model.Invoice.create(invoice_data)
    except model.InvalidInvoiceException as e:
        errors = e.args
        return make_response(jsonify(errors=errors), 400)
    return jsonify()

@api.route('/api/<id>/edit', methods=['POST'])
def edit(id):
    data = request.form.to_dict(flat=True)
    try:
        invoice_data = model.InvoiceApiModel.for_update(data, id)
        invoice = model.Invoice.update(invoice_data, id)
    except model.InvalidInvoiceException as e:
        errors = e.args
        return make_response(jsonify(errors=errors), 400)
    return jsonify()
