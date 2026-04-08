from django.db import migrations

def create_currencies(apps, schema_editor):
    Currency = apps.get_model('marketplace', 'Currency')
    currencies = [
        {"currency": "US Dollar", "iso_code": "USD", "symbol": "$"},
        {"currency": "Euro", "iso_code": "EUR", "symbol": "€"},
        {"currency": "British Pound", "iso_code": "GBP", "symbol": "£"},
        {"currency": "Malagasy Ariary", "iso_code": "MGA", "symbol": "Ar"},
        {"currency": "Kenyan Shilling", "iso_code": "KES", "symbol": "KSh"},
        {"currency": "Tanzanian Shilling", "iso_code": "TZS", "symbol": "TSh"},
    ]
    for c in currencies:
        Currency.objects.get_or_create(
            currency=c["currency"], 
            defaults={"iso_code": c["iso_code"], "symbol": c["symbol"]}
        )

class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0012_auto_20251208_1522'),  
    ]

    operations = [
        migrations.RunPython(create_currencies),
    ]
