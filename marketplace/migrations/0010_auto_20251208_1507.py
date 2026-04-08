from django.db import migrations

def create_units(apps, schema_editor):
    Unit = apps.get_model('marketplace', 'Unit')
    units = [
        {"unit": "Kilogramme", "abbreviation": "kg"},
        {"unit": "Grammes", "abbreviation": "g"},
        {"unit": "Litres", "abbreviation": "l"},
        {"unit": "Millilitres", "abbreviation": "ml"},
        {"unit": "Pièce", "abbreviation": "pc"},
        {"unit": "Mètre", "abbreviation": "m"},
        {"unit": "Centimètre", "abbreviation": "cm"},
        {"unit": "Paquet", "abbreviation": "pkt"},
        {"unit": "Boîte", "abbreviation": "bx"},
        {"unit": "Douzaine", "abbreviation": "dz"},
    ]
    for u in units:
        Unit.objects.get_or_create(unit=u['unit'], defaults={"abbreviation": u['abbreviation']})

class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0009_auto_20251208_1413'),  
    ]

    operations = [
        migrations.RunPython(create_units),
    ]
