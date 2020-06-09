from django.db.models.signals import post_delete
from django.dispatch import receiver
from main.models import Project
from utils import upload


@receiver(post_delete, sender=Project)
def order_picture_deleted(sender, instance, created=True, **kwargs):
    upload.delete_file(instance.file)
