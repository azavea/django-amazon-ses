"""Boto3 email backend class for Amazon SES."""
import boto3
import time

from botocore.exceptions import BotoCoreError, ClientError

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address
from django.dispatch import Signal

pre_send = Signal(providing_args=["message"])
post_send = Signal(providing_args=["message", "message_id"])


class EmailBackend(BaseEmailBackend):
    """An email backend for use with Amazon SES.

    Attributes:
        conn: A client connection for Amazon SES.
    """

    def __init__(
        self,
        fail_silently=False,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        **kwargs
    ):
        """Creates a client for the Amazon SES API.

        Args:
            fail_silently: Flag that determines whether Amazon SES
                client errors should throw an exception.

        """
        super().__init__(fail_silently=fail_silently)

        # Get configuration from AWS prefixed settings in settings.py
        access_key_id = getattr(settings, "AWS_ACCESS_KEY_ID", None)
        secret_access_key = getattr(settings, "AWS_SECRET_ACCESS_KEY", None)
        region_name = getattr(settings, "AWS_DEFAULT_REGION", "us-east-1")
        session_token = None

        # Override AWS prefixed configuration with Amazon SES-specific settings
        access_key_id = getattr(settings, "AWS_SES_ACCESS_KEY_ID", access_key_id)
        secret_access_key = getattr(
            settings, "AWS_SES_SECRET_ACCESS_KEY", secret_access_key
        )
        region_name = getattr(settings, "AWS_SES_REGION", region_name)
        self.configuration_set_name = getattr(
            settings, "AWS_SES_CONFIGURATION_SET_NAME", None
        )
        role_arn = getattr(settings, "AWS_SES_ROLE_ARN", None)
        external_id = getattr(settings, "AWS_SES_EXTERNAL_ID", None)

        # if a role ARN is defined, assume that role for
        # access_key/secret_access_key
        if role_arn is not None:
            sts = boto3.client(
                'sts',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region_name
            )
            session_name = 'django-amazon-ses-{}'.format(int(time. time()))
            assume_role_kwargs = {
                'RoleArn': role_arn,
                'RoleSessionName': session_name,
            }
            if external_id:
                assume_role_kwargs['ExternalId'] = external_id

            role = sts.assume_role(**assume_role_kwargs)
            access_key_id = role['Credentials']['AccessKeyId']
            secret_access_key = role['Credentials']['SecretAccessKey']
            session_token = role['Credentials']['SessionToken']

        # Override all previous configuration if settings provided
        # through the constructor
        if aws_access_key_id is not None and aws_secret_access_key is not None:
            access_key_id = aws_access_key_id
            secret_access_key = aws_secret_access_key
            session_token = kwargs.get('aws_session_token', None)

        self.conn = boto3.client(
            "ses",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            aws_session_token=session_token,
            region_name=region_name,
        )

    def send_messages(self, email_messages):
        """Sends one or more EmailMessage objects and returns the
        number of email messages sent.

        Args:
            email_messages: A list of Django EmailMessage objects.
        Returns:
            An integer count of the messages sent.
        Raises:
            ClientError: An interaction with the Amazon SES HTTP API
                failed.
        """
        if not email_messages:
            return 0

        sent_message_count = 0

        for email_message in email_messages:
            if self._send(email_message):
                sent_message_count += 1
        return sent_message_count

    def _send(self, email_message):
        """Sends an individual message via the Amazon SES HTTP API.

        Args:
            email_message: A single Django EmailMessage object.
        Returns:
            True if the EmailMessage was sent successfully, otherwise False.
        Raises:
            ClientError: An interaction with the Amazon SES HTTP API
                failed.
        """
        pre_send.send(self.__class__, message=email_message)

        if not email_message.recipients():
            return False

        from_email = sanitize_address(email_message.from_email, email_message.encoding)
        recipients = [
            sanitize_address(addr, email_message.encoding)
            for addr in email_message.recipients()
        ]
        message = email_message.message().as_bytes(linesep="\r\n")

        try:
            kwargs = {
                "Source": from_email,
                "Destinations": recipients,
                "RawMessage": {"Data": message},
            }

            if self.configuration_set_name is not None:
                kwargs["ConfigurationSetName"] = self.configuration_set_name

            result = self.conn.send_raw_email(**kwargs)
            message_id = result["MessageId"]
            post_send.send(self.__class__, message=email_message, message_id=message_id)
        except (ClientError, BotoCoreError):
            if not self.fail_silently:
                raise
            return False
        return True
