from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from users.models import UserActivation, MainUser, ProfileDocument, ProjectCategory
from main.tasks import send_email
from utils import emails, upload
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
        if created:
            activation = instance
            activation.is_active = False
            activation.save()


@receiver(pre_delete, sender=MainUser)
def user_pre_delete(sender, instance, created=True, **kwargs):
    if MainUser.profile.avatar:
        upload.delete_folder(MainUser.profile.avatar)
    doc = ProfileDocument.objects.filter(user=instance).first()
    if doc:
        upload.delete_folder(doc.document)


@receiver(pre_delete, sender=ProjectCategory)
def category_pre_delete(sender, instance, created=True, **kwargs):
    upload.delete_file(instance.image)

