# Generated by Django 4.2.6 on 2023-11-13 20:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio_planner', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mediagroup',
            options={'verbose_name_plural': 'Media Groups'},
        ),
        migrations.AlterField(
            model_name='brand',
            name='agency',
            field=models.ForeignKey(blank=True, help_text='The Agency that the Brand is managed by.', null=True, on_delete=django.db.models.deletion.CASCADE, to='portfolio_planner.agency'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='client_code',
            field=models.CharField(blank=True, help_text='Internal Client Code - for reference to system of record', max_length=191, null=True),
        ),
    ]
