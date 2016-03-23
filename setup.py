from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

tests_require = ['moto >= 0.4.23']

setup(
    name='django-amazon-ses',
    version='0.1.3',
    description='A Django email backend that uses Boto3 to interact with'
    'Amazon Simple Email Service (SES).',
    long_description=long_description,
    url='https://github.com/azavea/django-amazon-ses',
    author='Hector Castro',
    author_email='hcastro@azavea.com',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='django amazon ses email',
    packages=find_packages(exclude=['tests']),
    install_requires=['boto3 >= 1.3.0'],
    extras_require={
        'dev': [],
        'test': tests_require,
    },
    tests_require=tests_require,
)
