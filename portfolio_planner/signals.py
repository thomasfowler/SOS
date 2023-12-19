"""PortfolioPlanner signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Brand, BrandBusinessUnit


@receiver(post_save, sender=Brand)
def create_default_business_unit(sender, instance, created, **kwargs):
    if created:
        BrandBusinessUnit.objects.create(
            name='Default Business Unit',
            description='Automatically generated default business unit',
            brand=instance,
            user=instance.user
        )
