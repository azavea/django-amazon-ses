from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="django-amazon-ses",
    version="3.0.1",
    description="A Django email backend that uses Boto3 to interact with"
    "Amazon Simple Email Service (SES).",
    long_description=long_description,
    url="https://github.com/azavea/django-amazon-ses",
    author="Hector Castro",
    author_email="hcastro@azavea.com",
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="django amazon ses email",
    py_modules=["django_amazon_ses"],
    install_requires=["boto3>=1.3.0", "Django>=1.11,<3.1"],
    python_requires=">2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
)
