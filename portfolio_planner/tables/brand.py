from django.utils.translation import gettext_lazy as _
import django_tables2 as tables

from portfolio_planner.models import Brand


class BrandTable(tables.Table):
    """Brand Table."""

    class Meta:
        model = Brand
        template_name = "django_tables2/bootstrap5-responsive.html"

        fields = (
            'id',
            'name',
            'grow_bucket',
            'total_target',
            'total_revenue_last_fiscal',
            'status',
            'user',
            'agency',
            'org_business_unit.name',

        )

        attrs = {
            'class': 'table table-striped table-hover sos-table table-sm',
            'thead': {
                'class': 'thead-light'
            }
        }
