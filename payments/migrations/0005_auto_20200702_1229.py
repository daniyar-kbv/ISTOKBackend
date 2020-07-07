# Generated by Django 3.0.6 on 2020-07-02 06:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_auto_20200702_1225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectlinkedpaidfeatures',
            name='first_feature',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='main_paid_feature_1', to='payments.PaidFeatureType', verbose_name='Связаная услуга проекта 1'),
        ),
        migrations.AlterField(
            model_name='projectlinkedpaidfeatures',
            name='main_feature',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='linked_paid_features', to='payments.PaidFeatureType', verbose_name='Основная услуга проекта'),
        ),
        migrations.AlterField(
            model_name='projectlinkedpaidfeatures',
            name='second_feature',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='main_paid_feature_2', to='payments.PaidFeatureType', verbose_name='Связаная услуга проекта 2'),
        ),
    ]
