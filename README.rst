django-amazon-ses
=================

.. image:: https://github.com/azavea/django-amazon-ses/workflows/CI/badge.svg
    :target: https://github.com/azavea/django-amazon-ses/actions?query=workflow%3ACI
.. image:: https://api.codeclimate.com/v1/badges/b69dce91215b7003066b/maintainability
    :target: https://codeclimate.com/github/azavea/django-amazon-ses/maintainability
.. image:: https://api.codeclimate.com/v1/badges/b69dce91215b7003066b/test_coverage
    :target: https://codeclimate.com/github/azavea/django-amazon-ses/test_coverage

A Django email backend that uses `Boto 3 <https://boto3.readthedocs.io/en/latest/>`_ to interact with `Amazon Simple Email Service (SES) <https://aws.amazon.com/ses/>`_.

Table of Contents
-----------------

* `Installation <#installation>`_
* `AWS Credential Setup <#aws-credential-setup>`_

  * `AWS Named Profile <#aws-named-profile>`_
  * `AWS EC2 Instance Profile <#aws-ec2-instance-profile>`_

* `Django Configuration <#django-configuration>`_
* `Usage <#usage>`_
* `Signals <#signals>`_

  * `pre_send <#pre-send>`_
  * `post_send <#post-send>`_
   
* `Testing <#testing>`_

Installation
------------

First, install the Django Amazon SES email backend:

.. code:: bash

   $ pip install django-amazon-ses

Next, ensure that your Amazon Web Services (AWS) API credentials are setup, or that you are running on an Amazon EC2 instance with an instance profile that has access to the Amazon SES service.

AWS Credential Setup
--------------------

AWS Named Profile
*****************

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
--------------------

Lastly, override the ``EMAIL_BACKEND`` setting within your Django settings file:

.. code:: python

   EMAIL_BACKEND = 'django_amazon_ses.EmailBackend'

Optionally, you can set the AWS credentials. If unset, the backend will gracefully fall back to other Boto 3 credential providers.

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

If you want to force the use of a SES configuration set you can set the option below.
This is useful when you want to do more detailed tracking of your emails such as opens and clicks. You can see more details at: https://docs.aws.amazon.com/ses/latest/DeveloperGuide/using-configuration-sets.html.

.. code:: python

    AWS_SES_CONFIGURATION_SET_NAME = 'my_configuration_set'

Usage
-----

Once the configuration above is complete, use ``send_email`` to send email messages with Amazon SES from within your application:

.. code:: python

    from django.core.mail import send_mail

    send_mail(
        'Subject here',
        'Here is the message.',
        'from@example.com',
        ['to@example.com'],
        fail_silently=False,
    )

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
