# Generated by Django 3.0.6 on 2020-07-02 06:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_auto_20200702_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertransaction',
            name='feature',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='transactions', to='payments.UsersPaidFeature', verbose_name='Платная услуга'),
        ),
    ]
