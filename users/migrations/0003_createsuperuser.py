from __future__ import unicode_literals
from django.db import migrations, transaction
from users.models import User


def create_superuser(apps, schema_editor):
    with transaction.atomic():
        superuser = User()
        superuser.is_active = True
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.username = 'admin'
        superuser.email = 'admin@gmail.com'
        superuser.set_password('adminPassword')
        superuser.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_add_user_test_data'),
    ]

    operations = [
        migrations.RunPython(create_superuser)
    ]
