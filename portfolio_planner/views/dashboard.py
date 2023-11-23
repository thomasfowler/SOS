import json

from django.db.models import Sum
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django_tables2 import RequestConfig
from rolepermissions.checkers import has_role

from portfolio_planner.models import convert_to_money
from portfolio_planner.models import Brand
from portfolio_planner.models import FiscalYear
from portfolio_planner.models import Opportunity
from portfolio_planner.tables import BrandTable
from sos.roles import AccountManager, BusinessUnitHead, SalesDirector


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    """Dashboard View.

    Provides a Dashboard based on Brand level data.

    TODO: Rename this to Brand Dashboard.

    A note to the developer. You MUST update the dispatch method when you add further functions you want to route to.
    It's not magic. If you don't update the dispatch method, HTMX just end up in a loop re-rendering the entire template.
    """
    template_name = 'dashboard/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        """Dispatch requests to the appropriate method.

        Allows us to route the various HTMX requests to the appropriate method.

        Because the entire dashboard uses the same Brand roles based query, we can just use the same queryset for all.
        """
        # Perform the role based Brands query
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

        self.queryset = Brand.objects.filter(**filters)

        # Next, figure out the details we need allocate the brand into one of the G.R.O.W. buckets
        self.sum_target_values = Opportunity.objects.filter(brand__in=self.queryset).aggregate(
            total_target=Sum('target')
        )

        # Get current fiscal year so that we can get all the opportunities for the previous fiscal year
        current_fiscal_year = FiscalYear.objects.get(is_current=True)
        last_fiscal_year = FiscalYear.objects.get(year=current_fiscal_year.year - 1)

        all_revenue_last_fiscal = Opportunity.objects.filter(status__in=['active', 'won']).with_revenue(
            fiscal_year=last_fiscal_year).aggregate(_revenue_last_fiscal=Sum('total_revenue'))['_revenue_last_fiscal']

        # Loop through the opportunities and figure out if they are in a G.R.O.W. bucket
        for brand in self.queryset:
            # Get the sum target for all brand opportunities
            target = Opportunity.objects.filter(brand=brand).aggregate(total_target=Sum('target'))['total_target']

            # Get the revenue for all brand opportunities in the previous fiscal year
            # Note, total revenue needs to be annotated on the queryset so that we can use it in the aggregate
            revenue_last_fiscal = Opportunity.objects.filter(brand=brand, status__in=['active', 'won']).with_revenue(
                fiscal_year=last_fiscal_year).aggregate(_revenue_last_fiscal=Sum('total_revenue'))[
                '_revenue_last_fiscal']

            if target is not None and all_revenue_last_fiscal != 0 and target / all_revenue_last_fiscal >= 0.3:
                brand.grow_bucket = 'Game Changer'
            elif target is not None and revenue_last_fiscal != 0 and (
                    target - revenue_last_fiscal) / revenue_last_fiscal >= 0.1:
                brand.grow_bucket = 'Real Opportunity'
            elif revenue_last_fiscal is not None and revenue_last_fiscal > 0:
                brand.grow_bucket = 'Open'
            else:
                brand.grow_bucket = 'Wish'

            # Now append the financial data to the brand
            brand.total_target = convert_to_money(target) if target is not None else convert_to_money(0)
            brand.total_revenue_last_fiscal = convert_to_money(revenue_last_fiscal) if revenue_last_fiscal is not None else convert_to_money(0)

        # Route the request to the appropriate method
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

        # Initialize the table with the queryset
        table = BrandTable(self.queryset)

        # Apply sorting
        RequestConfig(request, paginate={'per_page': 10}).configure(table)

        # Include the URL parameters in the context for the template
        context = {
            'table': table,
        }

        return render(request, 'dashboard/components/brand_table.html', context)
