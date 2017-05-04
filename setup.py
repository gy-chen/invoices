from setuptools import setup, find_packages

setup(
    name='GYChen invoices manager project',
    version='0.0.1',
    author='GYChen',
    author_email='gy.chen@gms.nutc.edu.tw',
    license='GPL',
    packages=find_packages(),
    install_requires=[
        'flask',
        'oauth2client<4.0dev',
        'google-cloud',
        'six',
        'bs4',
        'html5lib'],
    entry_points={
        'console_scripts': [
            'gychen_invoices = invoices_gae.main:main',
        ],
    },
)
