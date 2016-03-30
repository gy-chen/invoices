from flask import Flask, render_template, request, redirect, url_for, g
import db, prizesparser, pagination

app = Flask(__name__)
# some constants
# error codes for invoices
NOT_VALID_YEAR = 1
NOT_VALID_MONTH = 2
NOT_VALID_NUMBER = 4

@app.before_request
def before_request():
    g.app = db.App.get_instance()

@app.route('/')
def index():
    # read pagination parameters
    non_matched_per_rows = request.args.get('non_matched_per_rows', pagination.Pagination.DEFAULT_PER_ROWS)
    non_matched_current_page = request.args.get('non_matched_page', 1)
    # sanitize pagination paramters
    try:
        non_matched_per_rows = int(non_matched_per_rows)
        non_matched_per_rows = pagination.Pagination.DEFAULT_PER_ROWS if non_matched_per_rows <= 0 else non_matched_per_rows
    except:
        non_matched_per_rows = pagination.Pagination.DEFAULT_PER_ROWS
    try:
        non_matched_current_page = int(non_matched_current_page)
        non_matched_current_page = 1 if non_matched_current_page < 1 else non_matched_current_page
    except:
        non_matched_current_page = 1
    # set pagination
    non_matched_invoices_query = g.app.get_non_matched_invoices()
    p = pagination.Pagination(non_matched_invoices_query.count(), non_matched_per_rows, non_matched_current_page)
    view_data = {
        'matched_invoices': g.app.get_matched_invoices().all(),
        'non_matched_invoices': non_matched_invoices_query[p.get_from_rows():p.get_to_rows() + 1],
        'pagination': p
        }
    # display matched, no-matched and non-matched invoices
    return render_template('index.html',
                           **view_data)

@app.route('/invoices')
def invoices():
    # read pagination parameters
    per_rows = request.args.get('per_rows', pagination.Pagination.DEFAULT_PER_ROWS)
    current_page = request.args.get('page', 1)
    # sanitize pagination parameters
    try:
        per_rows = int(per_rows)
        per_rows = pagination.Pagination.DEFAULT_PER_ROWS if per_rows <= 0 else per_rows
    except:
        per_rows = pagination.Pagination.DEFAULT_PER_ROWS
    try:
        current_page = int(current_page)
        current_page = 1 if current_page < 1 else current_page
    except:
        current_page = 1
    # set pagination
    invoices_query = g.app.get_invoices()
    invoices_count = invoices_query.count()
    p = pagination.Pagination(invoices_count, per_rows, current_page)
    # show invoices
    invoices = invoices_query[p.get_from_rows():p.get_to_rows() + 1]
    return render_template('invoices.html',
                           invoices=invoices,
                           pagination=p)
    

@app.route('/invoice_add', methods=['GET'])
def invoice_add_html():
    msg = request.args.get('msg', None)
    try:
        msg = int(msg)
    except:
        msg = None
    return render_template('invoice_add.html',
                           error_code={},
                           msg=msg)

@app.route('/invoice_add', methods=['POST'])
def invoice_add():
    # deal with user inputs
    # error code 1 year not valid
    # error code 2 month not valid
    # error code 4 number not valid
    # error code can plus together
    # my god jinj2 has no bitwise operators
    # use mapping instead
    error_code = {
        NOT_VALID_YEAR: False,
        NOT_VALID_MONTH: False,
        NOT_VALID_NUMBER: False
    }
    year = request.form['year'].strip()
    if not year.isdigit():
        error_code[NOT_VALID_YEAR] = True
    else:
        # sanilize
        year = int(year)
    month = request.form['month'].strip()
    if not month.isdigit():
        error_code[NOT_VALID_MONTH] = True
    else:
        month = int(month)
        if month < 1 or month > 6:
            error_code[NOT_VALID_MONTH] = True
    number = request.form['number'].strip()
    if not number.isdigit() or len(number) != 8:
        error_code[NOT_VALID_NUMBER] = True
    note = request.form['note'].strip()
    # inputs have some errors
    if True in error_code.values():
        return render_template('invoice_add.html',
                               error_code=error_code,
                               year=year,
                               month=month,
                               number=number,
                               note=note)
    # in this point, inputs are valid and have been sanilized.
    # write invoice data into database
    new_invoice = db.Invoice()
    new_invoice.year = year
    new_invoice.month = month
    new_invoice.number = number
    new_invoice.note = note
    db.session.add(new_invoice)
    db.session.commit()
    # redirect to avoid re-post
    return redirect(url_for('invoice_add_html') + '?msg=1')

@app.route('/invoice_delete/<invoice_number>', methods=['POST'])
def invoice_delete(invoice_number):
    target_invoice = db.session.query(db.Invoice).filter_by(id=invoice_number).one()
    db.session.delete(target_invoice)
    db.session.commit()
    back_url = request.referrer if request.referrer else '/'
    return redirect(back_url)

@app.route('/invoices_match', methods=['POST'])
def invoices_match():
    g.app.match_prizes()
    return redirect(url_for('index'))

@app.route('/prizes')
def prizes():
    data = {}
    data['prizes_update_date'] = g.app.prizes_last_modified_date
    prizesgroup = [] # [list of same date prizes, another list, ...]
    for prize_date in db.session.query(db.Prize.year, db.Prize.month).group_by(db.Prize.year, db.Prize.month).order_by(db.Prize.year.desc(), db.Prize.month.desc()).all():
        prize_year, prize_month = prize_date
        prizesgroup.append(db.session.query(db.Prize).filter(db.Prize.year == prize_year, db.Prize.month == prize_month).order_by(db.Prize.type_).all())
    # deal with pagination
    # read pagination parameters
    PRIZES_DEFAULT_PER_ROWS = 1 # default per rows for displaying prizes
    per_rows = request.args.get('per_rows', PRIZES_DEFAULT_PER_ROWS)
    current_page = request.args.get('page', 1)
    # sanitize pagination parameters
    try:
        per_rows = int(per_rows)
        per_rows = PRIZES_DEFAULT_PER_ROWS if per_rows <= 0 else per_rows
    except:
        per_rows = PRIZES_DEFAULT_PER_ROWS
    try:
        current_page = int(current_page)
        current_page = 1 if current_page < 1 else current_page
    except:
        current_page = 1
    # set pagination
    prizes_count = len(prizesgroup)
    p = pagination.Pagination(prizes_count, per_rows, current_page)
    data['pagination'] = p
    data['prizesgroup'] = prizesgroup[p.get_from_rows():p.get_to_rows() + 1]
    return render_template('prizes.html', **data)

@app.route('/prizes_update', methods=['POST'])
def prizes_update():
    g.app.update_prizes()
    return redirect(url_for('prizes'))

if __name__ == '__main__':
    app.debug = True
    app.run()
