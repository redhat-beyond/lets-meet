from django.db import migrations, transaction


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_user_username_user_name_user_phone_number_and_more'),
    ]

    def generate_user_test_data(apps, schema_editor):
        from users.models import User

        users_test_data = [
            ('testUser1', 'testUser1@mta.ac.il', 'PasswordU$er123', '0501111111'),
            ('testUser2', 'testUser2@mta.ac.il', 'PasswordU$er456', '0524444888'),
            ('testUser3', 'testUser3@mta.ac.il', 'PasswordU$er789', '0524444887')
        ]

        with transaction.atomic():
            for user_name, user_email, user_password, user_phone in users_test_data:
                user = User(name=user_name, email=user_email, password=user_password, phone_number=user_phone)
                user.save()

    operations = [
        migrations.RunPython(generate_user_test_data),
    ]
