from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from profiles.models import Application, ApplicationDocument, UsersPaidFeature
from main.tasks import deactivate_user_feature
from utils import upload
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import constants


@receiver(pre_delete, sender=Application)
def application_deleted(sender, instance, created=True, **kwargs):
    doc = ApplicationDocument.objects.filter(application=instance).first()
    if doc:
        upload.delete_folder(doc.document)


@receiver(post_save, sender=UsersPaidFeature)
def application_deleted(sender, instance, created=True, **kwargs):
    if created:
        # unit = instance.type.time_unit
        # amount = instance.type.time_amount
        # if unit == constants.TIME_DAY:
        #     delta = timedelta(days=amount)
        # elif unit == constants.TIME_MONTH:
        #     delta = relativedelta(months=+amount)
        # elif unit == constants.TIME_YEAR:
        #     delta = relativedelta(years=+amount)
        # else:
        delta = timedelta(seconds=10)
        instance.expires_at = instance.created_at + delta
        instance.save()
        deactivate_user_feature.apply_async(args=[instance.id], eta=instance.expires_at)
    profile = instance.user.profile
    profile.is_pro = instance.is_active
    profile.save()

