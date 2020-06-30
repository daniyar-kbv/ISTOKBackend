from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from main.models import Project, ProjectDocument, Render360, ProjectComment, ProjectCommentReply, \
    ProjectCommentDocument, ProjectCommentReplyDocument
from profiles.models import Notification
from utils import upload


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



