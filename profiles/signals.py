from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from profiles.models import Application, ApplicationDocument
from utils import upload


@receiver(pre_delete, sender=Application)
def application_deleted(sender, instance, created=True, **kwargs):
    doc = ApplicationDocument.objects.filter(application=instance).first()
    if doc:
        upload.delete_folder(doc.document)

