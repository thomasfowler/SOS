from django import forms

from portfolio_planner.models import Agency
from portfolio_planner.models import Brand
from portfolio_planner.models import Opportunity


class OpportunityForm(forms.ModelForm):
    """Form for creating a new Opportunity."""

    agency = forms.ModelChoiceField(
        queryset=Agency.objects.all(),
        required=False,
        help_text='Select an agency'
    )

    class Meta:
        """Metadata for the OpportunityForm."""
        model = Opportunity
        fields = [
            'description',
            'status',
            'brand',
            'business_unit',
            'product',
            'target',
            'fiscal_year',
        ]

    def __init__(self, *args, **kwargs):
        """Initialize the OpportunityForm."""
        super(OpportunityForm, self).__init__(*args, **kwargs)
        try:
            if self.instance and self.instance.brand:
                self.fields['agency'].initial = self.instance.brand.agency
        except Brand.DoesNotExist:
            pass

    def save(self, commit=True):
        """Save the Opportunity."""
        opportunity = super(OpportunityForm, self).save(commit=False)

        agency = self.cleaned_data.get('agency')
        if agency:
            # Assuming each brand is linked to one agency
            brand = Brand.objects.filter(agency=agency).first()
            if brand:
                opportunity.brand = brand

        if commit:
            opportunity.save()
        return opportunity
