from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from profiles.models import Application, ApplicationDocument, UsersPaidFeature, ProjectPaidFeature, Notification
from main.tasks import deactivate_user_feature, deactivate_project_feature, notify_project_feature, notify_user_feature
from utils import upload, general
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import constants


@receiver(pre_delete, sender=Application)
def application_deleted(sender, instance, created=True, **kwargs):
    doc = ApplicationDocument.objects.filter(application=instance).first()
    if doc:
        upload.delete_folder(doc.document)


@receiver(post_save, sender=Application)
def application_saved(sender, instance, created=True, **kwargs):
    client_text = f'Статус вашей заявки изменен на "{general.get_status_name(instance.client, instance)}"'
    merchant_text = f'Статус вашей заявки изменен на "{general.get_status_name(instance.merchant, instance)}"'
    Notification.objects.create(text=client_text, user=instance.client)
    Notification.objects.create(text=merchant_text, user=instance.merchant)


@receiver(post_save, sender=UsersPaidFeature)
def users_paid_feature_saved(sender, instance, created=True, **kwargs):
    if created:
        unit = instance.type.time_unit
        amount = instance.type.time_amount
        if unit == constants.TIME_DAY:
            delta = timedelta(days=amount)
        elif unit == constants.TIME_MONTH:
            delta = relativedelta(months=+amount)
        elif unit == constants.TIME_YEAR:
            delta = relativedelta(years=+amount)
        else:
            delta = timedelta(seconds=10)
        instance.expires_at = instance.created_at + delta
        instance.save()
        Notification.objects.create()
        notify_user_feature.apply_async(args=[instance.id], eta=(instance.expires_at - timedelta(days=1)))
        deactivate_user_feature.apply_async(args=[instance.id], eta=instance.expires_at)
    profile = instance.user.profile
    profile.is_pro = instance.is_active
    profile.save()


@receiver(post_save, sender=ProjectPaidFeature)
def project_paid_feature_saved(sender, instance, created=True, **kwargs):
    if created:
        unit = instance.type.time_unit
        amount = instance.type.time_amount
        if unit == constants.TIME_DAY:
            delta = timedelta(days=amount)
        elif unit == constants.TIME_MONTH:
            delta = relativedelta(months=+amount)
        elif unit == constants.TIME_YEAR:
            delta = relativedelta(years=+amount)
        else:
            delta = timedelta(seconds=10)
        instance.expires_at = instance.created_at + delta
        instance.save()
        notify_project_feature.apply_async(args=[instance.id], eta=(instance.expires_at - timedelta(days=1)))
        deactivate_project_feature.apply_async(args=[instance.id], eta=instance.expires_at)
    project = instance.project
    if instance.type.type == constants.PAID_FEATURE_TOP:
        project.is_top = instance.is_active
    elif instance.type.type == constants.PAID_FEATURE_DETAILED:
        project.is_detailed = instance.is_active
    project.save()

