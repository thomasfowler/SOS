"""URL configuration for sos project."""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from portfolio_planner.views.health import health_check_view
from portfolio_planner.views.home import HomeOrLoginView
from portfolio_planner.views.opportunity import OpportunityListView

urlpatterns = [
    # Auth
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html', next_page=None), name='logout'),
    # Site URLs
    path('', HomeOrLoginView.as_view(), name='home'),
    # Portfolio Planner
    path('opportunities/', OpportunityListView.as_view(), name='opportunity_list'),
    # Healthcheck
    path('health/', health_check_view, name='health_check'),
]

if settings.ADMIN_ENABLED:
    # Allow admin panel and browsable API auth
    urlpatterns.append(path('admin/', admin.site.urls, name='admin'))

urlpatterns += staticfiles_urlpatterns()
