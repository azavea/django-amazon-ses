django-amazon-ses
=================

A Django email backend that uses `Boto 3 <https://boto3.readthedocs.io/en/latest/>`_ to interact with `Amazon Simple Email Service (SES) <https://aws.amazon.com/ses/>`_.

Usage
-----

First, install the Django Amazon SES email backend:

.. code:: bash

   $ pip install django-amazon-ses

Next, ensure that your Amazon Web Services (AWS) API credentials are setup, or that you are running on an Amazon EC2 instance with an instance profile that has access to the Amazon SES service.

**Note**: Versions 1.0.x of ``django-amazon-ses`` are the last versions compatible with Django versions earlier than 1.11. If you are using Django versions earlier than 1.11.x, please pin your ``django-amazon-ses`` version.

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

   EMAIL_BACKEND = 'django_amazon_ses.EmailBackend'

Optionally, you can set the AWS credentials. If unset, the backend will
gracefully fall back to other Boto 3 credential providers.

.. code:: python

   AWS_ACCESS_KEY_ID = 'my_access_key...'
   AWS_SECRET_ACCESS_KEY = 'my_secret...'


Optionally, you can set the AWS region to be used (default is ``'us-east-1'``):

.. code:: python

   AWS_DEFAULT_REGION = 'eu-west-1'

Alternatively, provide AWS credentials using the settings below. This is useful in situations where you want to use separate credentials to send emails via SES than you would for other AWS services.

.. code:: python

    AWS_SES_ACCESS_KEY_ID = 'my_access_key...'
    AWS_SES_SECRET_ACCESS_KEY = 'my_secret...'
    AWS_SES_REGION = 'us-west-2'

Signals
-------

Two signals are provided for the backend, ``pre_send`` and ``post_send``. Both signals receive the message object being sent. The ``post_send`` signal also receives the Amazon SES message ID of the sent message.

pre_send
********

You can modify the email message on ``pre_send``. For example, if you have a blacklist of email addresses that should never receive emails, you can filter them from the recipients:

.. code:: python

    from django.dispatch.dispatcher import receiver
    from django_amazon_ses import pre_send

    @receiver(pre_send)
    def remove_blacklisted_emails(sender, message=None, **kwargs):
        blacklisted_emails = Blacklisted.objects.values_list('email', flat)
        message.to = [email for email in message.to if email not in blacklisted_emails]

If the ``pre_send`` receiver function ends up removing all of the recipients from the message, the email is not processed and the ``post_send`` signal is not sent.

post_send
*********

Similarly, the ``post_send`` signal can be used to log messages sent by the system. This is useful if you want to log the subject line of a message that bounced or received a complaint.

.. code:: python

    from django.dispatch.dispatcher import receiver
    from django.utils import timezone

    from django_amazon_ses import post_send

    @receiver(post_send)
    def log_message(sender, message=None, message_id=None, **kwargs):
        SentMessage.objects.create(
            subject = message.subject,
            body = message.body,
            message_id = message_id,
            date_sent = timezone.now()
        )

Testing
-------

The test suite execution process is managed by tox and takes care to mock out the Boto 3 interactions with Amazon's API, so there is no need for a valid set of credentials to execute it:

.. code:: bash

   $ tox
