from django.db import models

from django_use_email_as_username.models import BaseUser, BaseUserManager

from portfolio_planner.models import OrgBusinessUnit


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('business_unit', User.get_default_business_unit_id())
        return super().create_superuser(email, password, **extra_fields)


class User(BaseUser):
    """User model."""
    objects = CustomUserManager()

    business_unit = models.ForeignKey(
        OrgBusinessUnit,
        on_delete=models.CASCADE,
        related_name="users",
        # default=lambda: User.get_default_business_unit_id(),
    )

    @staticmethod
    def get_default_business_unit_id():
        """Get the default business unit ID."""
        default_unit, created = OrgBusinessUnit.objects.get_or_create(
            name="Default Business Unit",
            defaults={'status': 'active'}  # Add other default fields if necessary
        )
        return default_unit.id
