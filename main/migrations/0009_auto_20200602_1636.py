# Generated by Django 3.0.6 on 2020-06-02 10:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_projectcomment_projectcommentdocument_projectcommentreply_projectview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectcomment',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='main.Project', verbose_name='Проект'),
        ),
    ]
