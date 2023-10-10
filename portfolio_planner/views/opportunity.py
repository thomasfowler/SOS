import json

from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from portfolio_planner.models import Opportunity
from portfolio_planner.common import HtmxHttpRequest
from portfolio_planner.forms import OpportunityForm


@method_decorator(login_required, name='dispatch')
class PortfolioPlannerView(TemplateView):
    """Opportunity List View."""
    template_name = "portfolio_planner/portfolio_planner.html"


@login_required
@require_GET
def opportunity_list(request: HtmxHttpRequest) -> HttpResponse:
    """Opportunity List View."""
    opportunities = Opportunity.objects.all().order_by('id')
    return render(
        request,
        'portfolio_planner/opportunity_list.html',
        {'opportunities': opportunities}
    )


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

    return render(request, 'portfolio_planner/opportunity_form.html', {'form': form})


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

    return render(request, 'portfolio_planner/opportunity_form.html', {'form': form, 'opportunity': opportunity})


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