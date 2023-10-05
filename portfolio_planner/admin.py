from django.contrib import admin

import nested_admin

from .models import Agency
from .models import BusinessUnit
from .models import Client
from .models import Product
from .models import FiscalYear
from .models import Opportunity
from .models import OpportunityPerformance
from .models import PeriodPerformance


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    """Configuration of the Agency model in the Admin UI."""
    list_display = ('id', 'name', 'status', 'created', 'modified')
    list_filter = ('status',)
    search_fields = ('name', 'description',)
    ordering = ('-created',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'user', 'agency', 'created', 'modified')
    list_filter = ('status', 'user', 'agency',)
    search_fields = ('name', 'description',)
    ordering = ('-created',)
    raw_id_fields = ('user', 'agency',)


@admin.register(BusinessUnit)
class BusinessUnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'user', 'client', 'created', 'modified')
    list_filter = ('status', 'user', 'client',)
    search_fields = ('name', 'description',)
    ordering = ('-created',)
    raw_id_fields = ('user', 'client',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'created', 'modified')
    list_filter = ('status',)
    search_fields = ('name', 'description',)
    ordering = ('-created',)


@admin.register(FiscalYear)
class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ('id', 'year', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('year',)
    ordering = ('-year',)


@admin.register(PeriodPerformance)
class PeriodPerformanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'period', 'revenue')
    list_filter = ('period',)
    search_fields = ('period',)


# The next section deals with the Opportunity model and its related models.
class PeriodPerformanceInline(nested_admin.NestedTabularInline):
    model = PeriodPerformance
    extra = 1  # Number of empty rows displayed
    fields = ('period', 'revenue',)


class OpportunityPerformanceInline(nested_admin.NestedTabularInline):
    model = OpportunityPerformance
    extra = 1
    inlines = [PeriodPerformanceInline]


@admin.register(OpportunityPerformance)
class OpportunityPerformanceAdmin(nested_admin.NestedModelAdmin):
    list_display = ('opportunity', 'fiscal_year', 'total_revenue')  # Add fields that you find relevant here
    inlines = [PeriodPerformanceInline]


@admin.register(Opportunity)
class OpportunityAdmin(nested_admin.NestedModelAdmin):
    list_display = ('id', 'name', 'status', 'agency', 'client', 'business_unit', 'product', 'fiscal_year', 'target', 'approved')
    list_filter = ('status', 'agency', 'client', 'business_unit', 'product', 'fiscal_year', 'approved')
    search_fields = ('name', 'description')
    inlines = [OpportunityPerformanceInline]

