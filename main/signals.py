from django.db.models.signals import pre_delete
from django.dispatch import receiver
from main.models import Project, ProjectDocument
from utils import upload


@receiver(pre_delete, sender=Project)
def project_deleted(sender, instance, created=True, **kwargs):
    doc = ProjectDocument.objects.filter(project=instance).first()
    if doc:
        upload.delete_folder(doc.document)
