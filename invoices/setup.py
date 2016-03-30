from distutils.core import setup

setup(name='invoices',
      version='0.9',
      py_modules=['db', 'pagination', 'prizesgetter', 'prizesparser',
                  'web'],
      data_files=[('templates', ['templates/base.html',
                                 'templates/index.html',
                                 'templates/invoice_add.html',
                                 'templates/invoices.html',
                                 'templates/prizes.html']),
                  ('static', ['static/bootstrap/',
                              'static/font-awesome/',
                              'static/style.css'])]
      )
