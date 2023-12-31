from datetime import date
from decimal import Decimal
from logging import getLogger

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.db import IntegrityError
from django.db.models import Subquery, OuterRef, Sum, Value, Q, DecimalField
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _
from django_use_email_as_username.models import BaseUser, BaseUserManager
from djmoney.money import Money
from djmoney.models.fields import MoneyField
from djmoney.models.managers import understands_money
from model_utils import Choices
from model_utils.fields import StatusField
from model_utils.models import StatusModel
from model_utils.models import TimeStampedModel
from rolepermissions.checkers import has_role

from sos.roles import BusinessUnitHead, SalesDirector


logger = getLogger(__name__)


class User(BaseUser):
    """User model."""
    objects = BaseUserManager()

    def group_list(self):
        return "\n".join([g.name for g in self.groups.all()])


class MediaGroup(TimeStampedModel, StatusModel):
    """Media Group model.

    This is the holding company / group / parent of an individual agency.
    """

    STATUS = Choices(
        'active',
        'disabled',
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=191, help_text='Name of the parent agency', unique=True)
    description = models.TextField(blank=True, null=True, help_text='Description of the parent agency')
    status = StatusField(
        _('status'),
        default='active',
        help_text='Status of the parent agency. One of active or disabled'
    )

    class Meta:
        verbose_name_plural = 'Media Groups'

    def __str__(self):
        """Provide human readable representation."""
        return self.name


class Agency(TimeStampedModel, StatusModel):
    """Agency model."""

    STATUS = Choices(
        'active',
        'disabled',
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=191, help_text='Name of the agency', unique=True)
    description = models.TextField(blank=True, null=True, help_text='Description of the agency')
    status = StatusField(
        _('status'),
        default='active',
        help_text='Status of the agency. One of active or disabled'
    )
    media_group = models.ForeignKey(
        MediaGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='The parent agency if it exists'
    )

    class Meta:
        verbose_name_plural = 'Agencies'

    def __str__(self):
        """Provide human readable representation."""
        return self.name


class OrgBusinessUnit(TimeStampedModel, StatusModel):
    """Organisation Business Unit model."""

    STATUS = Choices(
        'active',
        'disabled',
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=191, help_text='Name of the business unit', unique=True)
    status = StatusField(
        _('status'),
        default='active',
        help_text='Status of the business unit. One of active or disabled'
    )
    business_unit_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='org_business_units',
        on_delete=models.CASCADE,
        help_text='The user that manages the business unit. Cannot be null.',
    )

    def save(self, *args, **kwargs):
        """Save the model."""
        if not (has_role(self.business_unit_manager, BusinessUnitHead) or
                has_role(self.business_unit_manager, SalesDirector)):
            raise ValidationError("Assigned user must have the BusinessUnitHead or SalesDirector role.")
        super(OrgBusinessUnit, self).save(*args, **kwargs)

    def __str__(self):
        """Provide human readable representation."""
        return self.name


class Brand(TimeStampedModel, StatusModel):
    """Brand model."""

    STATUS = Choices(
        'active',
        'disabled',
    )

    id = models.AutoField(primary_key=True)
    client_code = models.CharField(
        max_length=191,
        help_text='Internal Client Code - for reference to system of record',
        blank=True,
        null=True
    )
    name = models.CharField(max_length=191, help_text='Name of the Brand', unique=True)
    description = models.TextField(blank=True, null=True, help_text='Description of the Brand')
    status = StatusField(
        _('status'),
        default='active',
        help_text='Status of the Brand. One of active or disabled'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='brands', on_delete=models.CASCADE)
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text='The Agency that the Brand is managed by.',
    )
    org_business_unit = models.ForeignKey(
        OrgBusinessUnit,
        on_delete=models.CASCADE,
        help_text='The Organisation Business Unit that the Brand is managed by. Cannot be null.',
    )

    def __str__(self):
        """Provide human readable representation."""
        return self.name


class BrandBusinessUnit(TimeStampedModel, StatusModel):
    """Business Unit model."""

    STATUS = Choices(
        'active',
        'disabled',
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=191, help_text='Name of the business unit')
    description = models.TextField(blank=True, null=True, help_text='Description of the business unit')
    status = StatusField(
        _('status'),
        default='active',
        help_text='Status of the business unit. One of active or disabled'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='business_units',
        on_delete=models.CASCADE,
    )
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        """Save the model.

        If the user is not set, set it to the brand's user.
        """
        if self.user is None:
            self.user = self.brand.user
        super().save(*args, **kwargs)

    def __str__(self):
        """Provide human readable representation."""
        return f"{self.brand.name} - {self.name}"


class Product(TimeStampedModel):
    """Product model."""

    STATUS = Choices(
        'active',
        'disabled',
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=191, help_text='Name of the product', unique=True)
    description = models.TextField(blank=True, null=True, help_text='Description of the product')
    status = StatusField(
        _('status'),
        default='active',
        help_text='Status of the product. One of active or disabled'
    )

    def __str__(self):
        """Provide human readable representation."""
        return self.name


class FiscalYear(models.Model):
    """Fiscal Year model."""
    year = models.IntegerField(unique=True)
    is_current = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_current:
            # set all other records to is_current = False
            FiscalYear.objects.exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.year)


def get_current_fiscal_year():
    """Get the current fiscal year."""
    return FiscalYear.objects.get(is_current=True).id


def convert_to_money(value: Decimal, currency: str = 'ZAR') -> Money:
    """Convert the value to a money object."""

    # Assuming a uniform currency for simplicity
    # TODO: Add support for multiple currencies
    if value is not None and not isinstance(value, Money):
        return Money(Decimal(str(value)), currency)

    return value


class OpportunityQuerySet(models.QuerySet):
    """Opportunity QuerySet.

    Provides a method to annotate opportunities with other data such as revenue and agency information.
    """

    @understands_money
    def with_revenue(self, fiscal_year: FiscalYear):
        """Add revenue data to the queryset.

        Provides the following fields:
        - total_revenue: Sum all revenue for the opportunity
        - q1_revenue: Revenue in periods 1, 2 and 3
        - q2_revenue: Revenue in periods 4, 5 and 6
        - q3_revenue: Revenue in periods 7, 8 and 9
        - q4_revenue: Revenue in periods 10, 11 and 12
        - revenue_fiscal_year: The fiscal year that the revenue data is for

        TODO: We need to add in multi-currency support. Essentially, we need to annotate the currency type of the opp
            performance history and then allow for this
            We should also allow for the aggregation of multiple currencies into a single currency using an exchange
            rate table
        """
        zero_value = Value(Decimal('0.00'), output_field=DecimalField(max_digits=14, decimal_places=2))

        def quarterly_revenue_subquery(quarter):
            periods = {
                1: [1, 2, 3],
                2: [4, 5, 6],
                3: [7, 8, 9],
                4: [10, 11, 12]
            }.get(quarter, [])

            return Subquery(
                OpportunityPerformance.objects.filter(
                    opportunity=OuterRef('pk'),
                    fiscal_year=fiscal_year
                ).annotate(
                    quarterly_revenue=Coalesce(Sum(
                        'periods__revenue',
                        filter=Q(periods__period__in=periods),
                        output_field=MoneyField(
                            max_digits=14,
                            decimal_places=2,
                            default_currency='ZAR'
                        )
                    ),
                        zero_value
                    )
                ).values('quarterly_revenue')[:1]
            )

        return self.annotate(
            total_revenue=Coalesce(Sum('opportunityperformance__periods__revenue',
                                       output_field=DecimalField(max_digits=14, decimal_places=2)), zero_value),
            q1_revenue=quarterly_revenue_subquery(1),
            q2_revenue=quarterly_revenue_subquery(2),
            q3_revenue=quarterly_revenue_subquery(3),
            q4_revenue=quarterly_revenue_subquery(4),
            revenue_fiscal_year=Value(fiscal_year.year, output_field=models.IntegerField()),
        )

    def with_agency(self):
        """Add agency to the queryset."""
        return self.select_related('brand__agency').annotate(
            agency_name=models.F('brand__agency__name')
        )


class Opportunity(TimeStampedModel, StatusModel):
    """Opportunity model."""

    STATUS = Choices(
        'active',
        'disabled',
        'expired',
        'won',
        'lost',
        'abandoned',
    )

    id = models.AutoField(primary_key=True)
    description = models.TextField(blank=True, null=True, help_text='Description of the opportunity')
    status = StatusField(
        _('status'),
        default='active',
        help_text='Status of the opportunity. One of active, disabled, expired, won, lost or abandoned'
    )
    won_date = models.DateField(blank=True, null=True, help_text='Date the opportunity was won')
    lost_date = models.DateField(blank=True, null=True, help_text='Date the opportunity was lost')
    abandoned_date = models.DateField(blank=True, null=True, help_text='Date the opportunity was abandoned')
    disabled_date = models.DateField(blank=True, null=True, help_text='Date the opportunity was disabled')
    expired_date = models.DateField(blank=True, null=True, help_text='Date the opportunity expired')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    business_unit = models.ForeignKey(BrandBusinessUnit, null=True, blank=True, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    target = MoneyField(max_digits=14, decimal_places=2, default_currency='ZAR')
    fiscal_year = models.ForeignKey(FiscalYear, default=get_current_fiscal_year, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    approved_date = models.DateField(blank=True, null=True)
    approval_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='approved_opportunities',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Add extra fields to the model re revenue performance
    objects = OpportunityQuerySet.as_manager()

    class Meta:
        """Meta class."""

        # Make sure we can only have one opportunity per agency, brand, business unit, product and fiscal year.
        unique_together = (
            'brand',
            'business_unit',
            'product',
            'fiscal_year',
        )

        verbose_name_plural = 'Opportunities'

    def save(self, *args, **kwargs):
        # Check that the BusinessUnit is related to the Brand
        if self.business_unit and self.business_unit.brand != self.brand:
            raise IntegrityError("Business Unit must belong to the selected Brand")

        # Check if an instance with this primary key already exists
        if self.pk:
            try:
                original = Opportunity.objects.get(pk=self.pk)
                if self.status != original.status:
                    if self.status == 'won' and not self.won_date:
                        self.won_date = date.today()
                    elif self.status == 'lost' and not self.lost_date:
                        self.lost_date = date.today()
                    elif self.status == 'abandoned' and not self.abandoned_date:
                        self.abandoned_date = date.today()
                    elif self.status == 'disabled' and not self.disabled_date:
                        self.disabled_date = date.today()
                    elif self.status == 'expired' and not self.expired_date:
                        self.expired_date = date.today()
            except Opportunity.DoesNotExist:
                logger.warning(f"Opportunity with id {self.pk} does not exist. Status date not set.")
                pass

        # Set the approval date
        if self.approved and not self.approved_date:
            self.approved_date = date.today()

        super().save(*args, **kwargs)

    def __str__(self):
        """Provide human readable representation."""
        return f'{self.brand.name} - {self.product.name} - {self.fiscal_year.year}'


class OpportunityPerformance(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE)

    @property
    def total_revenue(self):
        """Get the total revenue for the opportunity performance.

        Uses the related name `periods` to get all the periods for the opportunity performance.
        """
        return self.periods.aggregate(Sum('revenue'))['revenue__sum'] or 0

    @property
    def q1_revenue(self):
        """Get Quarter 1 revenue for the opportunity performance."""
        return self.get_quarterly_revenue(1)

    @property
    def q2_revenue(self):
        """Get Quarter 2 revenue for the opportunity performance."""
        return self.get_quarterly_revenue(2)

    @property
    def q3_revenue(self):
        """Get Quarter 3 revenue for the opportunity performance."""
        return self.get_quarterly_revenue(3)

    @property
    def q4_revenue(self):
        """Get Quarter 4 revenue for the opportunity performance."""
        return self.get_quarterly_revenue(4)

    def get_quarterly_revenue(self, quarter: int):
        """Get the revenue for the given quarter."""
        if quarter == 1:
            periods = [1, 2, 3]
        elif quarter == 2:
            periods = [4, 5, 6]
        elif quarter == 3:
            periods = [7, 8, 9]
        elif quarter == 4:
            periods = [10, 11, 12]
        else:
            periods = []

        return self.periods.filter(period__in=periods).aggregate(Sum('revenue'))['revenue__sum'] or 0

    class Meta:
        unique_together = ('opportunity', 'fiscal_year')

    def __str__(self):
        return f"{self.opportunity} - {self.fiscal_year}"


class PeriodPerformance(models.Model):
    opportunity_performance = models.ForeignKey(OpportunityPerformance, related_name='periods', on_delete=models.CASCADE)
    period = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])  # Periods 1-12
    revenue = MoneyField(max_digits=14, decimal_places=2, default_currency='ZAR')
    fiscal_year = models.ForeignKey(
        FiscalYear,
        on_delete=models.CASCADE,
        default=get_current_fiscal_year
    )

    @property
    def calendar_month(self):
        fiscal_start = settings.FISCAL_YEAR_START_MONTH
        month = (self.period - 1 + fiscal_start - 1) % 12 + 1  # `- 1` and `+ 1` are for 0-based to 1-based conversion
        year = self.fiscal_year.year  # getting the year from the related FiscalYear instance
        return date(year, month, 1)

    class Meta:
        unique_together = ('opportunity_performance', 'period')

    def __str__(self):
        return f"{self.opportunity_performance} - Period {self.period} - {self.revenue}"
