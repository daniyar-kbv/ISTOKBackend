from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import UserActivation

from main.tasks import send_email

from utils import emails

import constants


@receiver(post_save, sender=UserActivation)
def activation_created(sender, instance, created=True, **kwargs):
    if instance:
        attrs_needed = ['_request', '_created']
        if all(hasattr(instance, attr) for attr in attrs_needed):
            if instance._created:
                send_email.delay(constants.ACTIVATION_EMAIL_SUBJECT,
                                 emails.generate_activation_email(instance.email, request=instance._request),
                                 instance.email)


@receiver(post_save, sender=UserActivation)
def activation_created(sender, instance, created, **kwargs):
    if instance:
        if created:
            activation = instance.activation
            activation.is_active = False
            activation.save()
