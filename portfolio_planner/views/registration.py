from django.conf import settings
from django.contrib.auth.views import PasswordResetView

from portfolio_planner.forms.registration import CustomPasswordResetForm


class CustomPasswordResetView(PasswordResetView):
    """Custom PasswordResetView to override the default template_name."""

    form_class = CustomPasswordResetForm
    from_email = settings.PASSWORD_RESET_EMAIL_FROM
