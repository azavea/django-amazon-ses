django-amazon-ses
=================

A Django email backend that uses Boto3 to interact with Amazon Simple Email Service (SES).

Usage
-----

First, install the Django Amazon SES email backend:

.. code:: bash

   $ pip install django-amazon-ses

Next, ensure that your Amazon Web Services API credentials are setup, or that you are running on an Amazon EC2 instance with an instance profile with access to the ``ses:SendRawEmail`` action:

.. code:: bash

   $ aws --profile test configure

Lastly, override the default SMTP ``EMAIL_BACKEND`` within your Django settings file:

.. code:: python

   AWS_PROFILE   = 'test'
   EMAIL_BACKEND = 'django_amazon_ses.backends.boto.EmailBackend'

Testing
-------

The test suite execution process is managed by tox and takes care to mock out the Boto interactions with Amazon's API, so there is no need for a valid set of credentials to execute it:

.. code:: bash

   $ tox
