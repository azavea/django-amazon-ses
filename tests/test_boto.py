import boto3
from botocore.exceptions import NoCredentialsError, ParamValidationError

from moto import mock_ses, mock_sts

from unittest import mock

from django.conf import settings
from django.core import mail
from django.core.mail import EmailMessage

from django.test import SimpleTestCase, override_settings

from django_amazon_ses import pre_send

settings.configure()

ROLE_ARN = 'arn:aws:iam::210987654321:role/ses_role'


@override_settings(AWS_SES_ROLE_ARN=ROLE_ARN)
class AssumeRoleTests(SimpleTestCase):
    @mock_sts
    @mock_ses
    def test_role_arn(self):
        """We can assume role."""
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

    @mock_sts
    def test_bad_role_arn(self):
        """We raise an exception on failure to assume role."""
        with self.assertRaises(ParamValidationError) as e:
            with override_settings(AWS_SES_ROLE_ARN='bad'):
                mail.get_connection("django_amazon_ses.EmailBackend")
        self.assertIn('Invalid length for parameter RoleArn', str(e.exception))

    @mock_sts
    @mock_ses
    def test_external_id(self):
        """We can assume role with external id."""
        client = boto3.client("ses", region_name="us-east-1")
        client.verify_email_identity(EmailAddress="bounce@example.com")

        with override_settings(AWS_SES_EXTERNAL_ID='1234'):
            conn = mail.get_connection("django_amazon_ses.EmailBackend")
        email = EmailMessage(
            "Subject",
            "Content",
            "bounce@example.com",
            ["to@example.com"],
            headers={"From": "from@example.com"},
        )
        self.assertGreater(conn.send_messages([email]), 0)

    @mock_sts
    def test_bad_external_id(self):
        """We raise an exception on failure to assume role with external id."""
        with self.assertRaises(ParamValidationError) as e:
            with override_settings(AWS_SES_EXTERNAL_ID='0'):
                mail.get_connection("django_amazon_ses.EmailBackend")
        self.assertIn('Invalid length for parameter ExternalId', str(e.exception))


class MailTests(SimpleTestCase):
    @mock_ses
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

    @mock_ses
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

    @mock_ses
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

    @mock_ses
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

    @mock_ses
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

    @mock_ses
    def test_send_messages_empty_list(self):
        conn = mail.get_connection("django_amazon_ses.EmailBackend")
        self.assertEqual(conn.send_messages([]), 0)
