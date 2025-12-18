from django.db import migrations

def create_post_statuses(apps, schema_editor):
    Post_status = apps.get_model('marketplace', 'Post_status')
    statuses = [
        {"name": "brouillon", "description": "Statut initial"},
        {"name": "published", "description": "Validé"},
        {"name": "négociation", "description": "En négociation"},
        {"name": "vendu", "description": "Post vendu"},
        {"name": "supprimé", "description": "Post supprimé"}
    ]
    for status in statuses:
        Post_status.objects.get_or_create(name=status['name'], defaults={"description": status['description']})

class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0003_alter_post_status_id'), 
    ]

    operations = [
        migrations.RunPython(create_post_statuses),
    ]
