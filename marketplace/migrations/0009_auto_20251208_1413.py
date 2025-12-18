from django.db import migrations
from django.utils import timezone
from django.contrib.auth.hashers import make_password

def create_categorie_users(apps, schema_editor):
    CategorieUser = apps.get_model('marketplace', 'CategorieUser')
    categories = ["Acheteur", "Vendeur", "User", "Admin"]
    for cat in categories:
        CategorieUser.objects.get_or_create(categorie=cat)

def create_users(apps, schema_editor):
    User = apps.get_model('marketplace', 'User')
    CategorieUser = apps.get_model('marketplace', 'CategorieUser')

    admin_category = CategorieUser.objects.get(categorie="Admin")
    User.objects.get_or_create(
        username="admin",
        defaults={
            "password": make_password("SmartSaha2025!"),  
            "first_name": "Super",
            "last_name": "Admin",
            "email": "smartsahaapp@gmail.com",
            "is_superuser": True,
            "is_staff": True,
            "is_active": True,
            "date_joined": timezone.now(),
            "id_categorie_user": admin_category,
            "is_verified": True
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0008_auto_20251203_1822'), 
    ]

    operations = [
        migrations.RunPython(create_categorie_users),
        migrations.RunPython(create_users),
    ]
