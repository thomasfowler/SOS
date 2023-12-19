# Generated by Django 4.2.7 on 2023-12-19 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio_planner', '0004_opportunity_approved_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agency',
            name='name',
            field=models.CharField(help_text='Name of the agency', max_length=191, unique=True),
        ),
        migrations.AlterField(
            model_name='brand',
            name='name',
            field=models.CharField(help_text='Name of the Brand', max_length=191, unique=True),
        ),
        migrations.AlterField(
            model_name='mediagroup',
            name='name',
            field=models.CharField(help_text='Name of the parent agency', max_length=191, unique=True),
        ),
        migrations.AlterField(
            model_name='orgbusinessunit',
            name='name',
            field=models.CharField(help_text='Name of the business unit', max_length=191, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(help_text='Name of the product', max_length=191, unique=True),
        ),
    ]