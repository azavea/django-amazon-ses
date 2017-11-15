from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='django-amazon-ses',
    version='0.3.2',
    description='A Django email backend that uses Boto3 to interact with'
    'Amazon Simple Email Service (SES).',
    long_description=long_description,
    url='https://github.com/azavea/django-amazon-ses',
    author='Hector Castro',
    author_email='hcastro@azavea.com',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='django amazon ses email',
    packages=find_packages(exclude=['tests']),
    install_requires=['boto3 >= 1.3.0'],
)
