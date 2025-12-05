
from django.db import migrations

def create_bid_statuses(apps, schema_editor):
    Bid_status = apps.get_model('marketplace', 'Bid_status')
    statuses = [
        {"name": "proposée", "description": "Statut initial de l'enchère"},
        {"name": "acceptée", "description": "Enchère acceptée"},
        {"name": "refusée", "description": "Enchère refusée"},
        {"name": "annulée", "description": "Enchère annulée par l'utilisateur"},
        {"name": "arrêtée", "description": "Négociation arrêtée définitivement"},
    ]

    for status in statuses:
        Bid_status.objects.get_or_create(
            name=status['name'],
            defaults={"description": status['description']}
        )

class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_auto_20251201_1341'),  # remplace par la dernière migration appliquée
    ]

    operations = [
        migrations.RunPython(create_bid_statuses),
    ]
