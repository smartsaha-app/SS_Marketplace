from django.db import migrations

def create_type_posts(apps, schema_editor):
    TypePost = apps.get_model('marketplace', 'TypePost')
    types = [
        "Selling",
        "Buying"
    ]
    for t in types:
        TypePost.objects.get_or_create(type=t)

class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0011_auto_20251208_1515'),  # remplace par ta dernière migration
    ]

    operations = [
        migrations.RunPython(create_type_posts),
    ]
