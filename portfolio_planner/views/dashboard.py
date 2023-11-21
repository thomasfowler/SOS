import json

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django_tables2 import RequestConfig
from rolepermissions.checkers import has_role

from portfolio_planner.models import Brand
from portfolio_planner.tables import BrandTable
from sos.roles import AccountManager, BusinessUnitHead, SalesDirector


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    """Dashboard View.

    A note to the developer. You MUST update the dispatch method when you add further functions you want to route to.
    It's not magic. If you don't update the dispatch method, HTMX just end up in a loop re-rendering the entire template.
    """
    template_name = 'dashboard/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        action = kwargs.get('action')

        if action == 'actual_vs_forecast':
            return self.actual_vs_forecast(request, *args, **kwargs)
        elif action == 'grow_status':
            return self.grow_status(request, *args, **kwargs)
        elif action == 'brand_table':
            # Pass the current_params to the brand_table method
            return self.brand_table(request,*args, **kwargs)

        return super().dispatch(request, *args, **kwargs)

    @method_decorator(require_GET)
    def actual_vs_forecast(self, request, *args, **kwargs) -> HttpResponse:
        period = request.GET.get('period', 'quarterly')

        # Dummy data. In reality, you'd fetch this based on the filter_type
        monthly_data = {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'datasets': [
                {'label': 'Actual', 'data': [12, 19, 3, 5, 2]},
                {'label': 'Forecast', 'data': [7, 11, 5, 8, 3]},
                {'label': 'Budget', 'data': [15, 13, 10, 9, 6]}
            ]
        }

        quarterly_data = {
            'labels': ['Quarter 1', 'Quarter 2', 'Quarter 3', 'Quarter 4'],
            'datasets': [
                {'label': 'Actual', 'data': [12, 19, 3, 5]},
                {'label': 'Forecast', 'data': [7, 11, 8, 3]},
                {'label': 'Budget', 'data': [13, 10, 9, 6]}
            ]
        }

        if period == 'monthly':
            chart_data = monthly_data
        else:
            chart_data = quarterly_data

        return render(request, 'dashboard/components/actual_vs_forecast.html', {'data': json.dumps(chart_data)})

    @method_decorator(require_GET)
    def grow_status(self, request, *args, **kwargs) -> HttpResponse:
        period = request.GET.get('period', 'annual')

        # Dummy Grow Data
        if period == 'annual':
            datasets = [
                {'label': 'Budget', 'data': [100, 200, 300, 400]},
                {'label': 'Actual', 'data': [110, 210, 290, 390]}
            ]
        elif period == 'q1':
            datasets = [
                {'label': 'Budget', 'data': [22, 45, 33, 50]},
                {'label': 'Actual', 'data': [20, 43, 35, 52]}
            ]
        elif period == 'q2':
            datasets = [
                {'label': 'Budget', 'data': [30, 48, 35, 47]},
                {'label': 'Actual', 'data': [29, 50, 33, 45]}
            ]
        elif period == 'q3':
            datasets = [
                {'label': 'Budget', 'data': [28, 49, 33, 45]},
                {'label': 'Actual', 'data': [27, 50, 31, 43]}
            ]
        elif period == 'q4':
            datasets = [
                {'label': 'Budget', 'data': [20, 58, 40, 48]},
                {'label': 'Actual', 'data': [24, 60, 38, 45]}
            ]
        elif period == 'current_month':
            datasets = [
                {'label': 'Budget', 'data': [5, 10, 8, 9]},
                {'label': 'Actual', 'data': [4, 11, 7, 8]}
            ]
        else:
            datasets = []

        chart_data = {
            'labels': [
                'Game Changer',
                'Real Opportunity',
                'Open',
                'Wish'
            ],
            'datasets': datasets
        }

        return render(request, 'dashboard/components/grow_status.html', {'data': json.dumps(chart_data)})

    @method_decorator(require_GET)
    def brand_table(self, request, *args, **kwargs) -> HttpResponse:
        """Brand Table."""

        user = request.user

        filters = {
            'status': 'active'
        }

        if has_role(user, AccountManager):
            filters['user'] = user
        elif has_role(user, BusinessUnitHead):
            filters['org_business_unit__business_unit_manager'] = user
        elif has_role(user, SalesDirector):
            pass  # No extra filter for SalesDirector, they see all opportunities
        else:
            return Brand.objects.none()  # If none of the roles apply, return no data

        queryset = Brand.objects.filter(**filters)

        # Initialize the table with the queryset
        table = BrandTable(queryset)

        # Apply sorting
        RequestConfig(request, paginate={'per_page': 10}).configure(table)

        # Include the URL parameters in the context for the template
        context = {
            'table': table,
        }

        return render(request, 'dashboard/components/brand_table.html', context)
