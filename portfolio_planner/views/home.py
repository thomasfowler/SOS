from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.db.models import Sum
from django_tables2 import RequestConfig
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView


from portfolio_planner.models import Brand
from portfolio_planner.models import convert_to_money
from portfolio_planner.models import FiscalYear
from portfolio_planner.models import Opportunity
from portfolio_planner.tables.opportunity import OpportunityApprovalsTable
from .helpers.brands import get_brand_role_filters
from .helpers.opportunities import role_based_opportunities


class HomeOrLoginView(UserPassesTestMixin, TemplateView):
    template_name = 'home/home.html'
    login_url = reverse_lazy('login')  # Redirect to login page if user fails the test function

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Set brand filters based on users current role
        filters = get_brand_role_filters(self.request.user)

        # Figure out the fiscals
        current_fiscal_year = FiscalYear.objects.get(is_current=True)
        last_fiscal_year = FiscalYear.objects.get(year=current_fiscal_year.year - 1)
        context['current_fiscal_year'] = current_fiscal_year
        context['last_fiscal_year'] = last_fiscal_year

        # Get the brands
        brands = Brand.objects.filter(**filters)

        # Count opportunities
        context['opportunities_count'] = Opportunity.objects.filter(brand__in=brands).count()
        context['opportunities_sum'] = convert_to_money(Opportunity.objects.filter(brand__in=brands).aggregate(Sum('target'))['target__sum'])

        # Calculate revenue
        context['revenue_last_fiscal'] = convert_to_money(Opportunity.objects.filter(status__in=['active', 'won']).with_revenue(
            fiscal_year=last_fiscal_year).aggregate(_revenue_last_fiscal=Sum('total_revenue'))[
            '_revenue_last_fiscal'])

        context['revenue_this_fiscal'] = convert_to_money(Opportunity.objects.filter(status__in=['active', 'won']).with_revenue(
            fiscal_year=current_fiscal_year).aggregate(_revenue_this_fiscal=Sum('total_revenue'))[
            '_revenue_this_fiscal'])

        # Count closed opportunities
        current_date = timezone.now().date()

        context['won_this_month_count'] = Opportunity.objects.filter(
            brand__in=brands,
            won_date__year=current_date.year,
            won_date__month=current_date.month,
        ).count()

        context['lost_this_month_count'] = Opportunity.objects.filter(
            brand__in=brands,
            lost_date__year=current_date.year,
            lost_date__month=current_date.month,
        ).count()

        context['abandoned_this_month_count'] = Opportunity.objects.filter(
            brand__in=brands,
            abandoned_date__year=current_date.year,
            abandoned_date__month=current_date.month,
        ).count()

        # Get the approvals values and counts
        context['unapproved_count'] = Opportunity.objects.filter(brand__in=brands, approved=False).count()
        context['approved_count'] = Opportunity.objects.filter(brand__in=brands, approved=True).count()
        context['approved_sum'] = convert_to_money(Opportunity.objects.filter(brand__in=brands, approved=True).aggregate(Sum('target'))['target__sum'])
        context['unapproved_sum'] = convert_to_money(Opportunity.objects.filter(brand__in=brands, approved=False).aggregate(Sum('target'))['target__sum'])

        # Render the approvals table
        tables_opps = Opportunity.objects.filter(brand__in=brands).with_revenue(last_fiscal_year).with_agency()
        for opp in tables_opps:
            opp.total_revenue = convert_to_money(opp.total_revenue)

        table = OpportunityApprovalsTable(tables_opps)

        # Apply sorting
        RequestConfig(self.request, paginate={'per_page': 20}).configure(table)
        context['table'] = table

        # Return context to the template
        from rolepermissions.roles import get_user_roles
        print(get_user_roles(self.request.user))
        return context

    def test_func(self):
        return self.request.user.is_authenticated
