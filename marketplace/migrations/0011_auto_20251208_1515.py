from django.db import migrations

def create_categorie_posts(apps, schema_editor):
    CategoriePost = apps.get_model('marketplace', 'CategoriePost')
    categories = [
        "Beans",
        "Cereals",
        "Fruits & Vegetables",
        "Nuts",
        "Spices",
        "Roots"
    ]
    for cat in categories:
        CategoriePost.objects.get_or_create(categorie=cat)

class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0010_auto_20251208_1507'),  # remplace par ta dernière migration
    ]

    operations = [
        migrations.RunPython(create_categorie_posts),
    ]
