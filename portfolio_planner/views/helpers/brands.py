
from rolepermissions.checkers import has_role

from portfolio_planner.models import Brand
from portfolio_planner.models import User
from sos.roles import AccountManager, BusinessUnitHead, SalesDirector


def get_brand_role_filters(user: User) -> dict:
    """Sets the correct brand filters based on the users role."""
    filters = {
        'status': 'active'
    }

    if has_role(user, AccountManager):
        filters['user'] = user
    elif has_role(user, BusinessUnitHead):
        filters['org_business_unit__business_unit_manager'] = user
    elif has_role(user, SalesDirector):
        pass  # No extra filter for SalesDirector, they see all opportunities

    return filters
