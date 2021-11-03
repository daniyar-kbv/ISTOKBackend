# Generated by Django 3.0.6 on 2020-07-03 05:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0013_auto_20200703_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='user_feature',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='transactions_as_users', to='payments.UsersPaidFeature', verbose_name='Платная услуга пользователя'),
        ),
    ]
