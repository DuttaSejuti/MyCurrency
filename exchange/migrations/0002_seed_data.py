from django.db import migrations

def seed_data(apps, schema_editor):
    Currency = apps.get_model('exchange', 'Currency')
    ExchangeRateProvider = apps.get_model('exchange', 'ExchangeRateProvider')

    currencies = [
        {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},
        {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'CHF'},
        {'code': 'USD', 'name': 'US Dollar', 'symbol': '$'},
        {'code': 'GBP', 'name': 'British Pound', 'symbol': '£'},
    ]
    for curr_data in currencies:
        Currency.objects.get_or_create(
            code=curr_data['code'],
            defaults={'name': curr_data['name'], 'symbol': curr_data['symbol']}
        )

    providers = [
        {
            'name': 'Currency Beacon',
            'adapter_key': 'currency_beacon',
            'priority': 10,
        },
        {
            'name': 'Mock Provider',
            'adapter_key': 'mock',
            'priority': 20,
        }
    ]
    for prov_data in providers:
        ExchangeRateProvider.objects.get_or_create(
            adapter_key=prov_data['adapter_key'],
            defaults={
                'name': prov_data['name'],
                'priority': prov_data['priority'],
                'is_active': True
            }
        )

def reverse_seed_data(apps, schema_editor):
    Currency = apps.get_model('exchange', 'Currency')
    ExchangeRateProvider = apps.get_model('exchange', 'ExchangeRateProvider')
    Currency.objects.filter(code__in=['EUR', 'CHF', 'USD', 'GBP']).delete()
    ExchangeRateProvider.objects.filter(adapter_key__in=['currency_beacon', 'mock']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_seed_data),
    ]
