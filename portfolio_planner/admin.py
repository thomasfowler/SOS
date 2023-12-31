from django.contrib import admin

import nested_admin
from django_use_email_as_username.admin import BaseUserAdmin
from rolepermissions.admin import RolePermissionsUserAdminMixin

from .models import Agency
from .models import BrandBusinessUnit
from .models import Brand
from .models import Product
from .models import FiscalYear
from .models import MediaGroup
from .models import Opportunity
from .models import OpportunityPerformance
from .models import OrgBusinessUnit
from .models import PeriodPerformance
from .models import User


# Custom User Admin based on django_use_email_as_username
# admin.site.register(User, BaseUserAdmin)
@admin.register(User)
class UserAdmin(RolePermissionsUserAdminMixin, BaseUserAdmin):
    """Custom User Admin based on django_use_email_as_username as well as RolePermissionAdmin."""

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'group_list')


@admin.register(MediaGroup)
class MediaGroupAdmin(admin.ModelAdmin):
    """Configuration of the Media Group model in the Admin UI."""
    list_display = ('id', 'name', 'status', 'created', 'modified')
    list_filter = ('status',)
    search_fields = ('name', 'description',)
    ordering = ('-created',)


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    """Configuration of the Agency model in the Admin UI."""
    list_display = ('id', 'name', 'media_group', 'status', 'created', 'modified')
    list_filter = ('status',)
    search_fields = ('name', 'description',)
    ordering = ('-created',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'user', 'agency', 'created', 'modified')
    list_filter = ('status', 'user', 'agency',)
    search_fields = ('name', 'description',)
    ordering = ('-created',)
    raw_id_fields = ('user', 'agency',)


@admin.register(BrandBusinessUnit)
class BrandBusinessUnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'user', 'brand', 'created', 'modified')
    list_filter = ('status', 'user', 'brand',)
    search_fields = ('name', 'description',)
    ordering = ('-created',)
    raw_id_fields = ('user', 'brand',)


@admin.register(OrgBusinessUnit)
class OrgBusinessUnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'business_unit_manager')
    list_filter = ('status', 'business_unit_manager')
    search_fields = ('name', 'business_unit_manager')


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
# We use nested_admin.NestedModelAdmin to display the related models in the
# Opportunity admin page.
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
    list_display = ('opportunity', 'fiscal_year', 'total_revenue')
    inlines = [PeriodPerformanceInline]


@admin.register(Opportunity)
class OpportunityAdmin(nested_admin.NestedModelAdmin):
    list_display = ('id', 'status', 'brand', 'business_unit', 'product', 'fiscal_year', 'target', 'approved')
    list_filter = ('status', 'brand', 'business_unit', 'product', 'fiscal_year', 'approved')
    search_fields = ('name', 'description')
    inlines = [OpportunityPerformanceInline]

