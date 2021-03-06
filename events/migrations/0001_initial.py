# Generated by Django 4.0.3 on 2022-03-28 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('location', models.CharField(blank=True, max_length=50)),
                ('description', models.TextField(blank=True)),
                ('date_time_start', models.DateTimeField()),
                ('date_time_end', models.DateTimeField()),
                ('color', models.CharField(choices=[('#FF0000', 'Red'), ('#FFC0CB', 'Pink'),
                 ('#FFA500', 'Orange'), ('#FFFF00', 'Yellow'), ('#800080', 'Purple'),
                 ('#008000', 'Green'), ('#0000FF', 'Blue'), ('#A52A2A', 'Brown'),
                 ('#FFFFFF', 'White'), ('#808080', 'Gray'), ('#000000', 'Black')],
                 default='#000000', max_length=7)),
            ],
        ),
    ]
