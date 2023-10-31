import json

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        action = kwargs.get('action')

        if action == 'actual_vs_forecast':
            return self.actual_vs_forecast(request, *args, **kwargs)

        return super().dispatch(request, *args, **kwargs)

    @method_decorator(require_GET)
    def actual_vs_forecast(self, request, *args, **kwargs) -> HttpResponse:
        period = request.GET.get('period', 'quarterly')

        # Dummy data. In reality, you'd fetch this based on the filter_type
        monthly_data = {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'datasets': [
                {'label': 'Actual', 'data': [12, 19, 3, 5, 2]},
                {'label': 'Forecast', 'data': [7, 11, 5, 8, 3]},
                {'label': 'Budget', 'data': [15, 13, 10, 9, 6]}
            ]
        }

        quarterly_data = {
            'labels': ['Quarter 1', 'Quarter 2', 'Quarter 3', 'Quarter 4'],
            'datasets': [
                {'label': 'Actual', 'data': [12, 19, 3, 5]},
                {'label': 'Forecast', 'data': [7, 11, 8, 3]},
                {'label': 'Budget', 'data': [13, 10, 9, 6]}
            ]
        }

        if period == 'monthly':
            chart_data = monthly_data
        else:
            chart_data = quarterly_data

        return render(request, 'dashboard/components/actual_vs_forecast.html', {'data': json.dumps(chart_data)})

