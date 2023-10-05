"""Health Check Views."""
from django.http import HttpResponse


def health_check_view(request):  # noqa pylint:disable=unused-argument
    """Return a 200 response with Healthy body for health checks."""
    return HttpResponse('Healthy')
