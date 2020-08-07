from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from main.models import Project, ProjectDocument, Render360, ProjectComment, ProjectCommentReply, \
    ProjectCommentDocument, ProjectCommentReplyDocument
from profiles.models import Notification
from utils import upload
from PIL import Image, ImageEnhance
from django.conf import settings
import os


@receiver(pre_delete, sender=Project)
def project_deleted(sender, instance, created=True, **kwargs):
    doc = ProjectDocument.objects.filter(project=instance).first()
    if doc:
        upload.delete_folder(doc.document)
    try:
        render = Render360.objects.get(project=instance)
        upload.delete_folder(render.document)
    except:
        pass


@receiver(pre_delete, sender=ProjectComment)
def project_comment_deleted(sender, instance, created=True, **kwargs):
    doc = ProjectCommentDocument.objects.filter(comment=instance).first()
    if doc:
        upload.delete_folder(doc.document)


@receiver(post_save, sender=ProjectCommentReply)
def project_comment_reply_saved(sender, instance, created=True, **kwargs):
    if created:
        text = f'На ваш комментарий "{instance.comment.text}" ответил специалист: "{instance.text}"'
        Notification.objects.create(user=instance.comment.user, text=text)


@receiver(pre_delete, sender=ProjectCommentReply)
def project_comment_reply_deleted(sender, instance, created=True, **kwargs):
    doc = ProjectCommentReplyDocument.objects.filter(reply=instance).first()
    if doc:
        upload.delete_folder(doc.document)

@receiver(post_save, sender=ProjectDocument)
def project_document_saved(sender, instance, created=True, **kwargs):
    if created:
        path_watermark = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT + '/watermark/watermark.png')
        watermark = Image.open(path_watermark)
        path_base_image = os.path.join(settings.BASE_DIR, instance.document.path)
        base_image = Image.open(path_base_image)
        if base_image.size[0]//3 < watermark.size[0] or base_image.size[1]//4 < watermark.size[1]:
            size = (base_image.size[0]//2, base_image.size[1]//3)
            watermark.thumbnail(size)
        watermark = watermark.copy()
        alpha = watermark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(1)
        watermark.putalpha(alpha)
        layer = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
        layer.paste(watermark, ((base_image.size[0]-watermark.size[0])//2, (base_image.size[1]-watermark.size[1])//2))
        Image.composite(layer, base_image, layer).save(path_base_image)
