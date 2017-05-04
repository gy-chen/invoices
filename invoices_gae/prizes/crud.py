#coding: utf-8`
from flask import Blueprint, request, render_template, redirect, url_for, current_app, Response
from . import model, helper
from ..auth import get_auth_manager_instance, oauth2

crud = Blueprint('prize_crud', __name__, template_folder='templates')

@crud.route('/')
@oauth2.required
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    prizes, next_page_token = model.Prize.list(cursor=token)

    # register filters
    current_app.jinja_env.filters['readable_month'] = helper.readable_month
    current_app.jinja_env.filters['readable_type'] = helper.readable_type
    current_app.jinja_env.filters['readable_prize'] = helper.readable_prize
    current_app.jinja_env.filters['group_by_date'] = helper.prizes_group_by_date
    return render_template(
        'prizes/list.html',
        prizes=prizes,
        next_page_token=next_page_token)

@crud.route('/tasks/fetch_prizes')
def task_fetch_prizes():
    model.Prize.auth_fetch_prizes()
    return Response(status=200)
