"""URL configuration for sos project."""
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path

from portfolio_planner.views.health import health_check_view

urlpatterns = [
    # Healthcheck
    path('health/', health_check_view, name='health_check'),
]

if settings.ADMIN_ENABLED:
    # Allow admin panel and browsable API auth
    urlpatterns.append(path('admin/', admin.site.urls, name='admin'))

urlpatterns += staticfiles_urlpatterns()
