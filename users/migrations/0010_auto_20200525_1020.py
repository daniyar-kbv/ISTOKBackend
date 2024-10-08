# Generated by Django 3.0.6 on 2020-05-25 10:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phone_field.models
import utils.upload
import utils.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20200522_0857'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='projectcategory',
            options={'verbose_name': 'Категория проектов', 'verbose_name_plural': 'Категории проектов'},
        ),
        migrations.AlterModelOptions(
            name='projectpurposesubtype',
            options={'verbose_name': 'Подтип назначения', 'verbose_name_plural': 'Подтипы назначения'},
        ),
        migrations.AlterModelOptions(
            name='projecttype',
            options={'verbose_name': 'Тип проекта', 'verbose_name_plural': 'Типы проекта'},
        ),
        migrations.AlterField(
            model_name='merchantprofile',
            name='categories',
            field=models.ManyToManyField(related_name='merchant_profiles', to='users.ProjectCategory', verbose_name='Категория'),
        ),
        migrations.AlterField(
            model_name='merchantprofile',
            name='specializations',
            field=models.ManyToManyField(related_name='merchant_profiles', to='users.Specialization', verbose_name='Специалиация'),
        ),
        migrations.AlterField(
            model_name='projectcategory',
            name='description',
            field=models.CharField(max_length=1000, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='projectcategory',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to=utils.upload.project_category_image_path, validators=[utils.validators.basic_validate_images, utils.validators.validate_file_size], verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='projectcategory',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='projecttag',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='users.ProjectCategory', verbose_name='Категория'),
        ),
        migrations.AlterField(
            model_name='specialization',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specializations', to='users.ProjectCategory', verbose_name='Категория'),
        ),
        migrations.CreateModel(
            name='CodeVerification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', phone_field.models.PhoneField(help_text='Номер телефона', max_length=31)),
                ('code', models.CharField(max_length=4, verbose_name='Код')),
                ('creation_date', models.DateTimeField(auto_now=True, verbose_name='Дата создания')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='code_verifications', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Подтпреждение номера телефона',
                'verbose_name_plural': 'Подтпреждения номеров телефона',
            },
        ),
    ]
