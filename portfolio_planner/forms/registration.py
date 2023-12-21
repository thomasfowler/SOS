"""Custom Registration Forms."""
from logging import getLogger

from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


logger = getLogger(__name__)


class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        # Your SendGrid API key
        sendgrid_api_key = settings.SENDGRID_API_KEY

        # Create the SendGrid Mail object with necessary details
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
        )

        # Get the current site domain
        domain = context.get('domain')

        # Construct the path for password reset confirmation
        uid = context.get('uid')  # The user's id encoded in base 64
        token = context.get('token')  # Token for password reset
        password_reset_confirm_path = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        # Construct the full reset URL
        # {{ protocol }}://{{ domain }}{% url 'password_reset_confirm' uidb64=uid token=token %}
        protocol = context.get('protocol', 'https')
        reset_url = f"{protocol}://{domain}{password_reset_confirm_path}"

        # SendGrid dynamic template data
        message.dynamic_template_data = {
            'first_name': context.get('user').first_name,
            'reset_url': reset_url,
        }

        # Set the template ID from SendGrid
        message.template_id = settings.PASSWORD_REST_EMAIL_TEMPLATE_ID

        # Send the email
        try:
            sg = SendGridAPIClient(sendgrid_api_key)
            response = sg.send(message)
            logger.info(f'Sent password reset email to {to_email}')
            logger.info(f'SendGrid response: {response.status_code}')
        except Exception as e:
            # Handle exceptions
            logger.error(e.message)
