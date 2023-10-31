"""URL configuration for sos project."""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from portfolio_planner.views.dashboard import DashboardView
from portfolio_planner.views.health import health_check_view
from portfolio_planner.views.home import HomeOrLoginView
from portfolio_planner.views.opportunity import PortfolioPlannerView
from portfolio_planner.views.opportunity import add_opportunity
from portfolio_planner.views.opportunity import OpportunityListView
from portfolio_planner.views.opportunity import edit_opportunity
from portfolio_planner.views.opportunity import remove_opportunity

urlpatterns = [
    # Auth
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html', next_page=None), name='logout'),
    # Site URLs
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
    # Healthcheck
    path('health/', health_check_view, name='health_check'),
]

if settings.ADMIN_ENABLED:
    # Allow admin panel and browsable API auth
    urlpatterns.append(path('admin/', admin.site.urls, name='admin'))

urlpatterns += staticfiles_urlpatterns()
