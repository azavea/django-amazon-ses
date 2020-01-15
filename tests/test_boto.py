import boto3
from botocore.exceptions import NoCredentialsError

from moto import mock_ses_deprecated

try:
    from unittest import mock
except ImportError:
    import mock

from django.conf import settings
from django.core import mail
from django.core.mail import EmailMessage

from django.test import SimpleTestCase

from django_amazon_ses import pre_send

settings.configure()


class MailTests(SimpleTestCase):
    @mock_ses_deprecated
    def test_custom_backend(self):
        """Test Amazon SES backend."""
        client = boto3.client("ses", region_name="us-east-1")
        client.verify_email_identity(EmailAddress="bounce@example.com")

        conn = mail.get_connection("django_amazon_ses.EmailBackend")
        email = EmailMessage(
            "Subject",
            "Content",
            "bounce@example.com",
            ["to@example.com"],
            headers={"From": "from@example.com"},
        )
        self.assertGreater(conn.send_messages([email]), 0)

    @mock_ses_deprecated
    @mock.patch("django_amazon_ses.pre_send.send")
    def test_signal_pre(self, mock_signal):
        client = boto3.client("ses", region_name="us-east-1")
        client.verify_email_identity(EmailAddress="bounce@example.com")

        conn = mail.get_connection("django_amazon_ses.EmailBackend")
        email = EmailMessage(
            "Subject",
            "Content",
            "bounce@example.com",
            ["to@example.com"],
            headers={"From": "from@example.com"},
        )
        conn.send_messages([email])
        called_args, called_kwargs = mock_signal.call_args
        self.assertIn("message", called_kwargs)
        self.assertEqual(email, called_kwargs["message"])

    @mock_ses_deprecated
    @mock.patch("django_amazon_ses.post_send.send")
    def test_signal_post(self, mock_signal):
        client = boto3.client("ses", region_name="us-east-1")
        client.verify_email_identity(EmailAddress="bounce@example.com")

        conn = mail.get_connection("django_amazon_ses.EmailBackend")
        email = EmailMessage(
            "Subject",
            "Content",
            "bounce@example.com",
            ["to@example.com"],
            headers={"From": "from@example.com"},
        )
        conn.send_messages([email])
        called_args, called_kwargs = mock_signal.call_args
        self.assertIn("message", called_kwargs)
        self.assertEqual(email, called_kwargs["message"])
        self.assertIn("message_id", called_kwargs)
        self.assertRegex(
            called_kwargs["message_id"],
            r"\w{16,16}-\w{8,8}-\w{4,4}-\w{4,4}-\w{4,4}-\w{12,12}-\w{6,6}",
        )

    @mock_ses_deprecated
    def test_pre_change_recipients(self):
        new_email_address = "changed@example.com"

        def change_recipients(sender, message=None, **kwargs):
            message.to = [new_email_address]

        pre_send.connect(change_recipients)

        client = boto3.client("ses", region_name="us-east-1")
        client.verify_email_identity(EmailAddress="bounce@example.com")

        conn = mail.get_connection("django_amazon_ses.EmailBackend")
        email = EmailMessage(
            "Subject",
            "Content",
            "bounce@example.com",
            ["to@example.com"],
            headers={"From": "from@example.com"},
        )
        self.assertNotEqual(email.to, [new_email_address])
        conn.send_messages([email])
        self.assertEqual(email.to, [new_email_address])

    @mock_ses_deprecated
    def test_pre_remove_recipients(self):
        def remove_recipients(sender, message=None, **kwargs):
            message.to = []

        pre_send.connect(remove_recipients)

        client = boto3.client("ses", region_name="us-east-1")
        client.verify_email_identity(EmailAddress="bounce@example.com")

        conn = mail.get_connection("django_amazon_ses.EmailBackend")
        email = EmailMessage(
            "Subject",
            "Content",
            "bounce@example.com",
            ["to@example.com"],
            headers={"From": "from@example.com"},
        )
        conn.send_messages([email])
        self.assertEqual(conn.send_messages([email]), 0)

    @mock.patch("botocore.client.BaseClient._make_api_call")
    def test_suppress_botocore_error(self, mock_make_api_call):
        """Ensure that fail_silently works when botocore raises an error."""
        mock_make_api_call.side_effect = NoCredentialsError

        conn = mail.get_connection("django_amazon_ses.EmailBackend")
        email = EmailMessage(
            "Subject",
            "Content",
            "bounce@example.com",
            ["to@example.com"],
            headers={"From": "from@example.com"},
        )

        self.assertFalse(conn.fail_silently)
        with self.assertRaises(NoCredentialsError):
            conn.send_messages([email])

        conn.fail_silently = True
        message_sent = conn.send_messages([email])
        self.assertFalse(message_sent)
