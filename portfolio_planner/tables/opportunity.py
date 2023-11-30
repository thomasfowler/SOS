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
            'status',
            'agency_name',
            'brand',
            'product',
            'target',
            'fiscal_year',
            'total_revenue',
            'approved',
            'buttons'
        )

        attrs = {
            'class': 'table table-striped table-hover sos-table table-sm',
            'thead': {
                'class': 'thead-light'
            }
        }


class OpportunityApprovalsTable(tables.Table):
    """Opportunity Approvals Table."""

    buttons = tables.TemplateColumn(
        template_name="home/partials/approvals_buttons.html",
        verbose_name=_("Actions"),
        orderable=False,
    )

    class Meta:
        model = Opportunity
        template_name = "django_tables2/bootstrap5-responsive.html"

        fields = (
            'id',
            'brand.user.first_name',
            'brand.user.last_name',
            'status',
            'agency_name',
            'brand',
            'product',
            'target',
            'total_revenue',
            'approved',
            'buttons'
        )

        attrs = {
            'class': 'table table-striped table-hover sos-table table-sm',
            'thead': {
                'class': 'thead-light'
            }
        }