import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3, unique=True)),
                ('name', models.CharField(db_index=True, max_length=20)),
                ('symbol', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name_plural': 'Currencies',
            },
        ),
        migrations.CreateModel(
            name='ExchangeRateProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('adapter_key', models.CharField(help_text='Internal identifier (e.g. currency_beacon)', max_length=50, unique=True)),
                ('priority', models.IntegerField(default=10)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['priority'],
            },
        ),
        migrations.CreateModel(
            name='CurrencyExchangeRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valuation_date', models.DateField(db_index=True)),
                ('rate_value', models.DecimalField(db_index=True, decimal_places=6, max_digits=18)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('exchanged_currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='exchanged_rates', to='exchange.currency')),
                ('source_currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='base_rates', to='exchange.currency')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rates_provider', to='exchange.exchangerateprovider')),
            ],
            options={
                'indexes': [models.Index(fields=['source_currency', 'exchanged_currency', 'valuation_date'], name='exchange_cu_source__c0be19_idx')],
                'constraints': [models.UniqueConstraint(fields=('source_currency', 'exchanged_currency', 'valuation_date', 'provider'), name='unique_exchange_rate')],
            },
        ),
    ]
