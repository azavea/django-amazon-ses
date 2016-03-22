import boto3

from moto import mock_ses

from django.conf import settings
from django.core import mail
from django.core.mail import EmailMessage

from django.test import SimpleTestCase

settings.configure(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
)


class MailTests(SimpleTestCase):
    @mock_ses
    def test_custom_backend(self):
        """Test Amazon SES backend."""
        client = boto3.client('ses', region_name='us-east-1')
        client.verify_email_identity(EmailAddress="bounce@example.com")

        conn = mail.get_connection(
            'django_amazon_ses.backends.boto.EmailBackend')
        email = EmailMessage(
            'Subject', 'Content', 'bounce@example.com', ['to@example.com'],
            headers={'From': 'from@example.com'},
        )
        self.assertGreater(conn.send_messages([email]), 0)
