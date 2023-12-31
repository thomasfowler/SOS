# Generated by Django 4.2.7 on 2023-11-18 14:22

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_use_email_as_username.models
import djmoney.models.fields
import model_utils.fields
import portfolio_planner.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django_use_email_as_username.models.BaseUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('status_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='status', verbose_name='status changed')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Name of the agency', max_length=191)),
                ('description', models.TextField(blank=True, help_text='Description of the agency', null=True)),
                ('status', model_utils.fields.StatusField(choices=[('active', 'active'), ('disabled', 'disabled')], default='active', help_text='Status of the agency. One of active or disabled', max_length=100, no_check_for_status=True, verbose_name='status')),
            ],
            options={
                'verbose_name_plural': 'Agencies',
            },
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('status_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='status', verbose_name='status changed')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('client_code', models.CharField(blank=True, help_text='Internal Client Code - for reference to system of record', max_length=191, null=True)),
                ('name', models.CharField(help_text='Name of the Brand', max_length=191)),
                ('description', models.TextField(blank=True, help_text='Description of the Brand', null=True)),
                ('status', model_utils.fields.StatusField(choices=[('active', 'active'), ('disabled', 'disabled')], default='active', help_text='Status of the Brand. One of active or disabled', max_length=100, no_check_for_status=True, verbose_name='status')),
                ('agency', models.ForeignKey(blank=True, help_text='The Agency that the Brand is managed by.', null=True, on_delete=django.db.models.deletion.CASCADE, to='portfolio_planner.agency')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BrandBusinessUnit',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('status_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='status', verbose_name='status changed')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Name of the business unit', max_length=191)),
                ('description', models.TextField(blank=True, help_text='Description of the business unit', null=True)),
                ('status', model_utils.fields.StatusField(choices=[('active', 'active'), ('disabled', 'disabled')], default='active', help_text='Status of the business unit. One of active or disabled', max_length=100, no_check_for_status=True, verbose_name='status')),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio_planner.brand')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_units', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FiscalYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(unique=True)),
                ('is_current', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='MediaGroup',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('status_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='status', verbose_name='status changed')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Name of the parent agency', max_length=191)),
                ('description', models.TextField(blank=True, help_text='Description of the parent agency', null=True)),
                ('status', model_utils.fields.StatusField(choices=[('active', 'active'), ('disabled', 'disabled')], default='active', help_text='Status of the parent agency. One of active or disabled', max_length=100, no_check_for_status=True, verbose_name='status')),
            ],
            options={
                'verbose_name_plural': 'Media Groups',
            },
        ),
        migrations.CreateModel(
            name='Opportunity',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('status_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='status', verbose_name='status changed')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, help_text='Description of the opportunity', null=True)),
                ('status', model_utils.fields.StatusField(choices=[('active', 'active'), ('disabled', 'disabled'), ('expired', 'expired'), ('won', 'won'), ('lost', 'lost'), ('abandoned', 'abandoned')], default='active', help_text='Status of the opportunity. One of active, disabled, expired, won, lost or abandoned', max_length=100, no_check_for_status=True, verbose_name='status')),
                ('target_currency', djmoney.models.fields.CurrencyField(choices=[('ZAR', 'South African Rand')], default='ZAR', editable=False, max_length=3)),
                ('target', djmoney.models.fields.MoneyField(decimal_places=2, default_currency='ZAR', max_digits=14)),
                ('approved', models.BooleanField(default=False)),
                ('approval_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approved_opportunities', to=settings.AUTH_USER_MODEL)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio_planner.brand')),
                ('business_unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='portfolio_planner.brandbusinessunit')),
                ('fiscal_year', models.ForeignKey(default=portfolio_planner.models.get_current_fiscal_year, on_delete=django.db.models.deletion.CASCADE, to='portfolio_planner.fiscalyear')),
            ],
            options={
                'verbose_name_plural': 'Opportunities',
            },
        ),
        migrations.CreateModel(
            name='OpportunityPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fiscal_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio_planner.fiscalyear')),
                ('opportunity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio_planner.opportunity')),
            ],
            options={
                'unique_together': {('opportunity', 'fiscal_year')},
            },
        ),
        migrations.CreateModel(
            name='OrgBusinessUnit',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('status_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='status', verbose_name='status changed')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Name of the business unit', max_length=191)),
                ('status', model_utils.fields.StatusField(choices=[('active', 'active'), ('disabled', 'disabled')], default='active', help_text='Status of the business unit. One of active or disabled', max_length=100, no_check_for_status=True, verbose_name='status')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Name of the product', max_length=191)),
                ('description', models.TextField(blank=True, help_text='Description of the product', null=True)),
                ('status', model_utils.fields.StatusField(choices=[('active', 'active'), ('disabled', 'disabled')], default='active', help_text='Status of the product. One of active or disabled', max_length=100, no_check_for_status=True, verbose_name='status')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='opportunity',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio_planner.product'),
        ),
        migrations.AddField(
            model_name='brand',
            name='org_business_unit',
            field=models.ForeignKey(help_text='The Organisation Business Unit that the Brand is managed by. Cannot be null.', on_delete=django.db.models.deletion.CASCADE, to='portfolio_planner.orgbusinessunit'),
        ),
        migrations.AddField(
            model_name='brand',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='brands', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='agency',
            name='media_group',
            field=models.ForeignKey(blank=True, help_text='The parent agency if it exists', null=True, on_delete=django.db.models.deletion.CASCADE, to='portfolio_planner.mediagroup'),
        ),
        migrations.CreateModel(
            name='PeriodPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)])),
                ('revenue_currency', djmoney.models.fields.CurrencyField(choices=[('ZAR', 'South African Rand')], default='ZAR', editable=False, max_length=3)),
                ('revenue', djmoney.models.fields.MoneyField(decimal_places=2, default_currency='ZAR', max_digits=14)),
                ('fiscal_year', models.ForeignKey(default=portfolio_planner.models.get_current_fiscal_year, on_delete=django.db.models.deletion.CASCADE, to='portfolio_planner.fiscalyear')),
                ('opportunity_performance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='periods', to='portfolio_planner.opportunityperformance')),
            ],
            options={
                'unique_together': {('opportunity_performance', 'period')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='opportunity',
            unique_together={('brand', 'business_unit', 'product', 'fiscal_year')},
        ),
    ]
