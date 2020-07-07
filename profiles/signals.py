from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from profiles.models import Application, ApplicationDocument, Notification
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

