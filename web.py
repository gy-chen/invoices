from flask import Flask, render_template, request, redirect, url_for
import db, prizesparser

app = Flask(__name__)
# some constants
# error codes for invoices
NOT_VALID_YEAR = 1
NOT_VALID_MONTH = 2
NOT_VALID_NUMBER = 4

@app.route('/')
def index():
    app = db.App.get_instance()
    view_data = {
        'matched_invoices': app.get_matched_invoices(),
        'no_matched_invoices': app.get_no_matched_invoices(),
        'non_matched_invoices': app.get_non_matched_invoices()
        }
    # display matched, no-matched and non-matched invoices
    return render_template('index.html',
                           **view_data)

@app.route('/invoices')
def invoices():
    # show all invoices
    invoices = db.session.query(db.Invoice)
    return render_template('invoices.html',
                           invoices=invoices)
    

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
    app = db.App.get_instance()
    app.match_prizes()
    return redirect(url_for('index'))

@app.route('/prizes')
def prizes():
    app = db.App.get_instance()
    data = {}
    data['prizes_update_date'] = app.prizes_last_modified_date
    prizesgroup = [] # [list of same date prizes, another list, ...]
    for prize_date in db.session.query(db.Prize.year, db.Prize.month).group_by(db.Prize.year, db.Prize.month).all():
        prize_year, prize_month = prize_date
        prizesgroup.append(db.session.query(db.Prize).filter(db.Prize.year == prize_year, db.Prize.month == prize_month).order_by(db.Prize.type_).all())
    data['prizesgroup'] = prizesgroup
    return render_template('prizes.html', **data)

@app.route('/prizes_update', methods=['POST'])
def prizes_update():
    app = db.App.get_instance()
    app.update_prizes()
    return redirect(url_for('prizes'))

if __name__ == '__main__':
    app.debug = True
    app.run()
