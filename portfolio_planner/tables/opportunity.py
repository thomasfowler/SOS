from django.utils.translation import gettext_lazy as _
import django_tables2 as tables

from portfolio_planner.models import Opportunity


class OpportunityTable(tables.Table):
    """Opportunity Table."""

    buttons = tables.TemplateColumn(
        template_name="portfolio_planner/opportunity/partials/buttons.html",
        verbose_name=_("Actions"),
        orderable=False,
    )

    class Meta:
        model = Opportunity
        template_name = "django_tables2/bootstrap5-responsive.html"

        fields = (
            'id',
            'description',
            'status',
            'agency_name',
            'brand',
            'business_unit',
            'product',
            'target',
            'fiscal_year',
            'total_revenue',
            'approved',
            'buttons'
        )

        attrs = {
            'class': 'table table-striped table-hover',
            'thead': {
                'class': 'thead-light'
            }
        }
