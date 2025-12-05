
from django.db import migrations

def create_message_statuses(apps, schema_editor):
    MessageStatus = apps.get_model('marketplace', 'Message_status')

    statuses = [
        {"status": "ouvert", "expiration": 30},
        {"status": "fermé", "expiration": 0},
        {"status": "expiré", "expiration": 0},
    ]

    for s in statuses:
        MessageStatus.objects.get_or_create(
            status=s["status"],
            defaults={"expiration": s["expiration"]}
        )

class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0006_user_is_verified'),  # mets ici la dernière migration
    ]

    operations = [
        migrations.RunPython(create_message_statuses),
    ]
