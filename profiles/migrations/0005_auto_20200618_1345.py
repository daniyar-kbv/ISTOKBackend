# Generated by Django 3.0.6 on 2020-06-18 07:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_application_applicationdocument'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='application',
            options={'ordering': ['-creation_date'], 'verbose_name': 'Заявка', 'verbose_name_plural': 'Заявки'},
        ),
    ]
