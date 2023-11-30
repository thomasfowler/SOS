from datetime import datetime, timedelta

from django.conf import settings
from django.db.models import Count
from django.db.models import Sum
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django_tables2 import RequestConfig
import simplejson as json

from portfolio_planner.models import convert_to_money
from portfolio_planner.models import Brand
from portfolio_planner.models import FiscalYear
from portfolio_planner.models import Opportunity
from portfolio_planner.tables import BrandTable
from .helpers.brands import get_brand_role_filters


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
        filters = get_brand_role_filters(request.user)

        self.queryset = Brand.objects.filter(**filters)

        # Next, figure out the details we need allocate the brand into one of the G.R.O.W. buckets
        self.sum_target_values = Opportunity.objects.filter(brand__in=self.queryset).aggregate(
            total_target=Sum('target')
        )

        # Get current fiscal year so that we can get all the opportunities for the previous fiscal year
        self.current_fiscal_year = FiscalYear.objects.get(is_current=True)
        self.last_fiscal_year = FiscalYear.objects.get(year=self.current_fiscal_year.year - 1)

        all_revenue_last_fiscal = Opportunity.objects.filter(status__in=['active', 'won']).with_revenue(
            fiscal_year=self.last_fiscal_year).aggregate(_revenue_last_fiscal=Sum('total_revenue'))['_revenue_last_fiscal']

        # Set some default values for the G.R.O.W. buckets. We will add to these in the brand loop below
        self.game_changer_target = convert_to_money(0)
        self.real_opportunity_target = convert_to_money(0)
        self.open_target = convert_to_money(0)
        self.wish_target = convert_to_money(0)

        self.game_changer_revenue_last_fiscal = convert_to_money(0)
        self.real_opportunity_revenue_last_fiscal = convert_to_money(0)
        self.open_revenue_last_fiscal = convert_to_money(0)
        self.wish_revenue_last_fiscal = convert_to_money(0)

        # Loop through the opportunities and figure out if they are in a G.R.O.W. bucket
        for brand in self.queryset:
            # Get the sum target for all brand opportunities
            target = Opportunity.objects.filter(brand=brand).aggregate(total_target=Sum('target'))['total_target']

            # Get the revenue for all brand opportunities in the previous fiscal year
            # Note, total revenue needs to be annotated on the queryset so that we can use it in the aggregate
            revenue_last_fiscal = Opportunity.objects.filter(brand=brand, status__in=['active', 'won']).with_revenue(
                fiscal_year=self.last_fiscal_year).aggregate(_revenue_last_fiscal=Sum('total_revenue'))[
                '_revenue_last_fiscal']

            # Guard for revenue_last_fiscal being None
            revenue_last_fiscal = 0 if revenue_last_fiscal is None else revenue_last_fiscal

            if target is not None and all_revenue_last_fiscal != 0 and target / all_revenue_last_fiscal >= 0.3:
                brand.grow_bucket = 'Game Changer'
                self.game_changer_target += convert_to_money(target)
                self.game_changer_revenue_last_fiscal += convert_to_money(revenue_last_fiscal)
            elif target is not None and revenue_last_fiscal != 0 and (
                    target - revenue_last_fiscal) / revenue_last_fiscal >= 0.1:
                brand.grow_bucket = 'Real Opportunity'
                self.real_opportunity_target += convert_to_money(target)
                self.real_opportunity_revenue_last_fiscal += convert_to_money(revenue_last_fiscal)
            elif revenue_last_fiscal is not None and revenue_last_fiscal > 0:
                brand.grow_bucket = 'Open'
                self.open_target += convert_to_money(target)
                self.open_revenue_last_fiscal += convert_to_money(revenue_last_fiscal)
            else:
                brand.grow_bucket = 'Wish'
                # Check for None values and set to 0
                if target is None:
                    target = 0
                self.wish_target += convert_to_money(target)
                self.wish_revenue_last_fiscal += convert_to_money(revenue_last_fiscal)

            # Now append the financial data to the brand
            brand.total_target = convert_to_money(target) if target is not None else convert_to_money(0)
            brand.total_revenue_last_fiscal = convert_to_money(revenue_last_fiscal) if revenue_last_fiscal is not None else convert_to_money(0)

        # Route the request to the appropriate method
        action = kwargs.get('action')

        if action == 'top_brands':
            return self.top_brands(request, *args, **kwargs)
        elif action == 'grow_status':
            return self.grow_status(request, *args, **kwargs)
        elif action == 'brand_table':
            # Pass the current_params to the brand_table method
            return self.brand_table(request,*args, **kwargs)
        elif action == 'time_remaining':
            return self.time_remaining(request, *args, **kwargs)
        elif action == 'opportunities_status':
            return self.opportunities_status(request, *args, **kwargs)

        # Just run this function if we don't have an action. This renders the base template for the dashboard
        return super().dispatch(request, *args, **kwargs)

    @method_decorator(require_GET)
    def top_brands(self, request, *args, **kwargs) -> HttpResponse:
        # Get the number of brands to display from the request, default to 5
        number_brands = int(request.GET.get('number', 5))

        # Calculate the sum of target values for opportunities per brand
        brand_targets = (
            Opportunity.objects.filter(brand__in=self.queryset)
            .values('brand__name')  # Assuming the brand has a 'name' field to display
            .annotate(total_target=Sum('target'))
            .order_by('-total_target')[:number_brands]
        )

        # Get the total for the top 'n' brands
        top_brands_total = sum(item['total_target'] for item in brand_targets)

        # Calculate the 'other' category total
        other_total = self.sum_target_values['total_target'] - top_brands_total

        # Prepare the data for the pie chart
        labels = [item['brand__name'] for item in brand_targets] + ['Other']
        data = [item['total_target'] for item in brand_targets] + [other_total]

        context = {
            'labels': labels,
            'data': json.dumps(data, use_decimal=True),
            'number_brands': number_brands,
        }

        return render(request, 'dashboard/components/top_brands.html', context)

    @method_decorator(require_GET)
    def grow_status(self, request, *args, **kwargs) -> HttpResponse:
        """Grow Status Chart.

        Period selection supports value one of period, q1, q2, q3, q4, current_month
        TODO: Have temporarily removed quarterly options until data model supports it
        """
        period = request.GET.get('period', 'annual')

        # Dummy Grow Data
        if period == 'annual':
            datasets = [
                {'label': 'Target', 'data': [
                    self.game_changer_target.amount,
                    self.real_opportunity_target.amount,
                    self.open_target.amount,
                    self.wish_target.amount
                ]
                 },
                {'label': 'Last Fiscal', 'data': [
                    self.game_changer_revenue_last_fiscal.amount,
                    self.real_opportunity_revenue_last_fiscal.amount,
                    self.open_revenue_last_fiscal.amount,
                    self.wish_revenue_last_fiscal.amount
                ]
                 }
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
        data = json.dumps(chart_data, use_decimal=True)

        return render(request, 'dashboard/components/grow_status.html', {'data': data})

    @method_decorator(require_GET)
    def brand_table(self, request, *args, **kwargs) -> HttpResponse:
        """Brand Table."""

        # Initialize the table with the queryset
        table = BrandTable(self.queryset)

        # Apply sorting
        RequestConfig(request, paginate={'per_page': 20}).configure(table)

        # Include the URL parameters in the context for the template
        context = {
            'table': table,
        }

        return render(request, 'dashboard/components/brand_table.html', context)

    @method_decorator(require_GET)
    def time_remaining(self, request, *args, **kwargs) -> HttpResponse:
        """Time Remaining Chart."""

        # Get today's date
        today = datetime.now()

        # Determine the end of the current fiscal year
        fiscal_year_end_year = today.year if today.month < settings.FISCAL_YEAR_START_MONTH else today.year + 1
        fiscal_year_end_date = datetime(fiscal_year_end_year, settings.FISCAL_YEAR_START_MONTH - 1, 28)

        # Calculate remaining time
        remaining = fiscal_year_end_date - today
        remaining_days = remaining.days
        remaining_weeks = remaining_days // 7
        remaining_months = (fiscal_year_end_date.year - today.year) * 12 + fiscal_year_end_date.month - today.month

        # Adjust for current week (assuming 5 working days per week)
        remaining_days_adjusted = remaining_days + (5 - today.weekday() if today.weekday() < 5 else 0)

        # Now, lets provide these as percentages of the total time as well as the elapsed time. And round them to
        # full values
        remaining_days_percentage = round(remaining_days_adjusted / 240 * 100)  # 240 working days in a year
        remaining_weeks_percentage = round(remaining_weeks / 52 * 100)
        remaining_months_percentage = round(remaining_months / 12 * 100)

        elapsed_days_percentage = 100 - remaining_days_percentage
        elapsed_weeks_percentage = 100 - remaining_weeks_percentage
        elapsed_months_percentage = 100 - remaining_months_percentage

        context = {
            'remaining_days': remaining_days,
            'remaining_weeks': remaining_weeks,
            'remaining_months': remaining_months,
            'elapsed_days': 240 - remaining_days_adjusted,
            'elapsed_weeks': 52 - remaining_weeks,
            'elapsed_months': 12 - remaining_months,
            'remaining_days_adjusted': remaining_days_adjusted,
            'remaining_days_percentage': remaining_days_percentage,
            'remaining_weeks_percentage': remaining_weeks_percentage,
            'remaining_months_percentage': remaining_months_percentage,
            'elapsed_days_percentage': elapsed_days_percentage,
            'elapsed_weeks_percentage': elapsed_weeks_percentage,
            'elapsed_months_percentage': elapsed_months_percentage,
        }

        return render(request, 'dashboard/components/time_remaining.html', context)

    @method_decorator(require_GET)
    def opportunities_status(self, request, *args, **kwargs) -> HttpResponse:
        """Opportunities Status Chart."""
        queryset = Opportunity.objects.filter(brand__in=self.queryset)
        status_counts = queryset.values('status').annotate(count=Count('status')).order_by()

        # Prepare data for the pie chart
        labels = [status['status'] for status in status_counts]
        data = [status['count'] for status in status_counts]

        # Pass the data to the template
        context = {
            'labels': labels,
            'data': data,
        }

        return render(request, 'dashboard/components/opportunities_status.html', context)
