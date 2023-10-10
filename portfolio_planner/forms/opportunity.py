from django import forms

from portfolio_planner.models import Opportunity


class OpportunityForm(forms.ModelForm):
    """Form for creating a new Opportunity."""

    class Meta:
        """Metadata for the OpportunityForm."""
        model = Opportunity
        fields = [
            'name',
            'description',
            'status',
            'agency',
            'client',
            'business_unit',
            'product',
            'target',
            'fiscal_year',
        ]
