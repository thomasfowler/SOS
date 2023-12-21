"""URL configuration for sos project."""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from portfolio_planner.views.dashboard import DashboardView
from portfolio_planner.views.health import health_check_view
from portfolio_planner.views.home import HomeOrLoginView
from portfolio_planner.views.opportunity import approve_opportunity
from portfolio_planner.views.opportunity import PortfolioPlannerView
from portfolio_planner.views.opportunity import add_opportunity
from portfolio_planner.views.opportunity import OpportunityListView
from portfolio_planner.views.opportunity import edit_opportunity
from portfolio_planner.views.opportunity import remove_opportunity
from portfolio_planner.views.opportunity import filtered_brands
from portfolio_planner.views.opportunity import filtered_business_units
from portfolio_planner.views.registration import CustomPasswordResetView

urlpatterns = [
    # Auth
    path(
        'login/', auth_views.LoginView.as_view(),
        name='login'
    ),
    path(
        'logout/', auth_views.LogoutView.as_view(
            template_name='registration/login.html', next_page='home'),
        name='logout'
    ),
    # Password Reset
    # Sends user an email with a link to reset their password.
    # Uses a custom class so we can send using Sendgrid
    path(
        "password_reset/", CustomPasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
        ),
        name="password_reset"
    ),
    # Simple page to confirm that the password reset email has been sent
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html',
        ),
        name="password_reset_done",
    ),
    # Page to enter new password. Requires uidb64 and token from email link
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
        ),
        name="password_reset_confirm",
    ),
    # Page to confirm that the password has been reset
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html',
        ),
        name="password_reset_complete",
    ),
    # Site URLs
    # home
    path('', HomeOrLoginView.as_view(), name='home'),
    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/<str:action>/', DashboardView.as_view(), name='dashboard_action'),
    # Portfolio Planner
    path('portfolio-planner/', PortfolioPlannerView.as_view(), name='portfolio_planner'),
    path('opportunities/', OpportunityListView.as_view(), name='opportunity_list'),
    path('opportunities/add/', add_opportunity, name='add_opportunity'),
    path('opportunities/<int:opportunity_id>/edit/', edit_opportunity, name='edit_opportunity'),
    path('opportunities/<int:opportunity_id>/remove/', remove_opportunity, name='remove_opportunity'),
    path('opportunities/<int:opportunity_id>/approve/', approve_opportunity, name='approve_opportunity'),
    path('opportunities/filtered-brands/', filtered_brands, name='filtered_brands'),
    path('opportunities/filtered-bus/', filtered_business_units, name='filtered_business_units'),
    # Healthcheck
    path('health/', health_check_view, name='health_check'),
]

if settings.ADMIN_ENABLED:
    # Allow admin panel and browsable API auth
    urlpatterns.append(path('admin/', admin.site.urls, name='admin'))

urlpatterns += staticfiles_urlpatterns()
