django-amazon-ses
=================

A Django email backend that uses `Boto 3 <https://boto3.readthedocs.io/en/latest/>`_ to interact with `Amazon Simple Email Service (SES) <https://aws.amazon.com/ses/>`_.

Usage
-----

First, install the Django Amazon SES email backend:

.. code:: bash

   $ pip install django-amazon-ses

Next, ensure that your Amazon Web Services (AWS) API credentials are setup, or that you are running on an Amazon EC2 instance with an instance profile that has access to the Amazon SES service.

AWS API Credential Setup
************************

Create an AWS API credential profile named ``test`` using the `AWS CLI <https://aws.amazon.com/cli/>`_:

.. code:: bash

   $ aws --profile test configure

Ensure that the ``AWS_PROFILE`` environment variable is set so that Boto 3 knows which credentials profile to use:

.. code:: bash

   $ AWS_PROFILE="test" gunicorn my:app

AWS EC2 Instance Profile
************************

Create an `instance profile <http://docs.aws.amazon.com/codedeploy/latest/userguide/how-to-create-iam-instance-profile.html>`_ with at least the ``ses:SendRawEmail`` action. Then, associate it with the instance/s running your application. An example policy that enables access to the ``ses:SendRawEmail`` action is below:

.. code:: javascript

   {
      "Version": "2012-10-17",
      "Statement": [
         {
            "Effect": "Allow",
            "Action": ["ses:SendRawEmail"],
            "Resource":"*"
         }
      ]
   }

Django Configuration
********************

Lastly, override the ``EMAIL_BACKEND`` setting within your Django settings file:

.. code:: python

   EMAIL_BACKEND = 'django_amazon_ses.backends.boto.EmailBackend'

Testing
-------

The test suite execution process is managed by tox and takes care to mock out the Boto 3 interactions with Amazon's API, so there is no need for a valid set of credentials to execute it:

.. code:: bash

   $ tox
