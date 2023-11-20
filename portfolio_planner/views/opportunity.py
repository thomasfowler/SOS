import json

from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django_tables2 import SingleTableView
from rolepermissions.checkers import has_role

from portfolio_planner.models import Brand
from portfolio_planner.models import BrandBusinessUnit
from portfolio_planner.models import Opportunity
from portfolio_planner.common import HtmxHttpRequest
from portfolio_planner.forms import OpportunityForm
from portfolio_planner.tables import OpportunityTable
from sos.roles import AccountManager, BusinessUnitHead, SalesDirector


@method_decorator(login_required, name='dispatch')
class PortfolioPlannerView(TemplateView):
    """Opportunity List View."""
    template_name = "portfolio_planner/portfolio_planner.html"

    def get_context_data(self, **kwargs):
        """Get Context Data.

        We are currently using this to grab the URL params and make them available to OpportunityListView template
        via HTMX injection. If we ever need to strip out or manage the params, we can do this here.
        """
        context = super().get_context_data(**kwargs)
        context['current_params'] = self.request.GET.urlencode()
        return context


@method_decorator(login_required, name='dispatch')
class OpportunityListView(SingleTableView):
    """Opportunity List View."""
    model = Opportunity
    table_class = OpportunityTable
    template_name = "portfolio_planner/opportunity/opportunity_list.html"

    def get_table_data(self):
        """Get Table Data.

        Filters opportunities based on role.

        Account Managers can only see their owned opportunities.
        Business Unit Heads can see all opportunities owned by their business unit.
        Sales Directors can see all opportunities.
        """
        if has_role(self.request.user, AccountManager):
            return Opportunity.objects.filter(brand__user=self.request.user)
        elif has_role(self.request.user, BusinessUnitHead):
            return Opportunity.objects.filter(brand__org_business_unit__business_unit_manager=self.request.user)
        elif has_role(self.request.user, SalesDirector):
            return Opportunity.objects.all()
        else:
            return Opportunity.objects.none()


@login_required
@require_http_methods(['GET', 'POST'])
def add_opportunity(request: HtmxHttpRequest) -> HttpResponse:
    """Add Opportunity View."""
    if request.method == 'POST':
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps(
                        {
                            "opportunityListChanged": None,
                            "showMessage": f'{opportunity.name} created successfully.'
                        }
                    )
                }
            )
    else:
        form = OpportunityForm()

    return render(request, 'portfolio_planner/opportunity/opportunity_form.html', {'form': form})


@login_required
@require_http_methods(['GET', 'POST'])
def edit_opportunity(request: HtmxHttpRequest, opportunity_id: int) -> HttpResponse:
    """Edit an opportunity."""
    opportunity = Opportunity.objects.get(id=opportunity_id)
    if request.method == 'POST':
        form = OpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            opportunity = form.save()
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps(
                        {
                            "opportunityListChanged": None,
                            "showMessage": f'{opportunity.name} updated successfully.'
                        }
                    )
                }
            )
    else:
        form = OpportunityForm(instance=opportunity)

    return render(request, 'portfolio_planner/opportunity/opportunity_form.html', {'form': form, 'opportunity': opportunity})


@login_required
@require_POST
def remove_opportunity(request: HtmxHttpRequest, opportunity_id: int) -> HttpResponse:
    """Remove an opportunity."""
    opportunity = Opportunity.objects.get(id=opportunity_id)
    opportunity.delete()
    return HttpResponse(
        status=204,
        headers={
            'HX-Trigger': json.dumps(
                {
                    "opportunityListChanged": None,
                    "showMessage": f'{opportunity.name} deleted successfully.'
                }
            )
        }
    )


@login_required
@require_GET
def filtered_brands(request: HtmxHttpRequest) -> HttpResponse:
    """Get brands for a given agency."""
    agency_id = request.GET.get('agency')

    # Try filter for agency_id. But if we dont have one, just supply all the brands
    if agency_id:
        brands = Brand.objects.filter(agency_id=agency_id)
    else:
        brands = Brand.objects.all()

    context = {
        'brands': brands
    }

    return render(
        request,
        'portfolio_planner/opportunity/partials/brand_dropdown.html',
        context
    )


@login_required
@require_GET
def filtered_business_units(request: HtmxHttpRequest) -> HttpResponse:
    """Get business units for a given brand."""

    brand_id = request.GET.get('brand')

    # Unlike with brands, we need to be careful about brand BUs.
    # We should only return if we get a match to ensure we have referential integrity
    if brand_id:
        business_units = BrandBusinessUnit.objects.filter(brand_id=brand_id)
    else:
        business_units = BrandBusinessUnit.objects.none()

    context = {
        'business_units': business_units
    }

    return render(
        request,
        'portfolio_planner/opportunity/partials/business_unit_dropdown.html',
        context
    )
