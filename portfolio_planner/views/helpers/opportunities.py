from django.conf import settings
from django.db.models import QuerySet
from django.db.models import Sum
from rolepermissions.checkers import has_role

from portfolio_planner.models import convert_to_money
from portfolio_planner.models import FiscalYear
from portfolio_planner.models import Opportunity
from sos.roles import AccountManager, BusinessUnitHead, SalesDirector


def role_based_opportunities(user: settings.AUTH_USER_MODEL) -> QuerySet:
    """
    Return Opportunities queryset based on Role.

    Account Managers can only see their owned opportunities.
    Business Unit Heads can see all opportunities owned by their business unit.
    Sales Directors can see all opportunities.

    Includes revenue data for the previous fiscal year.
    """

    # We want revenue from the previous fiscal year
    current_fiscal_year = FiscalYear.objects.get(is_current=True)
    last_fiscal_year = FiscalYear.objects.get(year=current_fiscal_year.year - 1)

    filters = {
        'status__in': ['active', 'won', 'lost'],
        'fiscal_year': current_fiscal_year
    }

    if has_role(user, AccountManager):
        filters['brand__user'] = user
    elif has_role(user, BusinessUnitHead):
        filters['brand__org_business_unit__business_unit_manager'] = user
    elif has_role(user, SalesDirector):
        pass  # No extra filter for SalesDirector, they see all opportunities
    else:
        return Opportunity.objects.none()  # If none of the roles apply, return no data

    queryset = Opportunity.objects.filter(**filters).with_revenue(last_fiscal_year).with_agency()

    # Convert revenue to Money object
    # For some reason, we cannot get the queryset to return a Money type object. So we are converting it here.
    for opp in queryset:
        opp.total_revenue = convert_to_money(opp.total_revenue)

    return queryset


def categorise_opportunities(opportunities: QuerySet) -> QuerySet:
    # TODO: This is supposed to be at the brand level, not the opportunity level
    #   Leaving this here for short term reference.
    current_fiscal_year = FiscalYear.objects.get(is_current=True)
    last_fiscal_year = FiscalYear.objects.get(year=current_fiscal_year.year - 1)

    all_open_opportunities = Opportunity.objects.filter(
        status__in=['active', 'won', 'lost'], fiscal_year=current_fiscal_year
    )

    revenue_last_fiscal = all_open_opportunities.aggregate(Sum('total_revenue'))['total_revenue__sum']

    for opp in opportunities:
        if opp.target / revenue_last_fiscal >= 0.3:
            opp.grow_status = 'Game Changer'
        elif (opp.target - opp.total_revenue) / opp.total_revenue >= 0.1:
            opp.grow_status = 'Real Opportunity'
