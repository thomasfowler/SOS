from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from portfolio_planner.models import Opportunity


@method_decorator(login_required, name='dispatch')
class OpportunityListView(ListView):
    model = Opportunity
    template_name = "portfolio_planner/opportunity_list.html"
    context_object_name = "opportunities"
