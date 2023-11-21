from django.conf import settings
from django.db.models import QuerySet
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
    """
    extra_filters = {}

    if has_role(user, AccountManager):
        extra_filters = {'brand__user': user}
    elif has_role(user, BusinessUnitHead):
        extra_filters = {'brand__org_business_unit__business_unit_manager': user}
    elif has_role(user, SalesDirector):
        pass  # No extra filter for SalesDirector, they see all opportunities
    else:
        return Opportunity.objects.none()  # If none of the roles apply, return no data

    # We want revenue from the previous fiscal year
    current_fiscal_year = FiscalYear.objects.get(is_current=True)
    last_fiscal_year = FiscalYear.objects.get(year=current_fiscal_year.year - 1)
    queryset = Opportunity.objects.with_revenue(last_fiscal_year, extra_filters).with_agency()

    # Convert revenue to Money object
    # For some reason, we cannot get the queryset to return a Money type object. So we are converting it here.
    for opp in queryset:
        opp.total_revenue = convert_to_money(opp.total_revenue)

    return queryset
