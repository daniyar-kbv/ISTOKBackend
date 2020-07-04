from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from profiles.models import Notification
from payments.models import UsersPaidFeature, ProjectPaidFeature, ProjectLinkedPaidFeatures
from main.tasks import deactivate_user_feature, deactivate_project_feature, notify_project_feature, notify_user_feature
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import constants


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
        Notification.objects.create(user=instance.user, text=f'{constants.NOTIFICATION_FEATURE_CREATED} Про аккаунт')
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
        Notification.objects.create(user=instance.project.user, text=f'{constants.NOTIFICATION_FEATURE_CREATED} {constants.PAID_FEATURE_TYPES[instance.type.type][1]}')
        notify_project_feature.apply_async(args=[instance.id], eta=(instance.expires_at - timedelta(days=1)))
        deactivate_project_feature.apply_async(args=[instance.id], eta=instance.expires_at)
    project = instance.project
    if instance.type.type == constants.PAID_FEATURE_TOP:
        project.is_top = instance.is_active
    elif instance.type.type == constants.PAID_FEATURE_DETAILED:
        project.is_detailed = instance.is_active
    project.save()


@receiver(post_save, sender=ProjectLinkedPaidFeatures)
def linked_feature_saved(sender, instance, created=True, **kwargs):
    feature = instance.main_feature
    first_feature = instance.first_feature
    second_feature = instance.second_feature
    feature.type = constants.PAID_FEATURE_TOP_DETAILED
    feature.text = f'{first_feature.text}\n{second_feature.text}'
    feature.price = first_feature.price + second_feature.price
    feature.time_amount = first_feature.time_amount
    feature.time_unit = first_feature.time_unit
    feature.beneficial = first_feature.beneficial
    feature.position = first_feature.position
    feature.save()
