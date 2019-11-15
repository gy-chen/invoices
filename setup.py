from io import open

from setuptools import find_packages, setup

with open("invoices/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.strip().split("=")[1].strip(" '\"")
            break
    else:
        version = "0.0.1"

REQUIRES = [
    "pyzbar",
    "sqlalchemy",
    "flask",
    "flask_sqlalchemy",
    "flask_wtf",
    "jwt",
    "requests_oauthlib",
    "scrapy",
    "Flask-Migrate",
    "Pillow",
    'uwsgi',
    'gevent',
]

setup(
    name="invoices",
    version=version,
    description="",
    author="GYCHEN",
    author_email="gy.chen@gms.nutc.edu.tw",
    maintainer="GYCHEN",
    maintainer_email="gy.chen@gms.nutc.edu.tw",
    url="https://github.com/gy-chen/invoices",
    install_requires=REQUIRES,
    tests_require=["coverage", "pytest"],
    packages=find_packages(),
)
