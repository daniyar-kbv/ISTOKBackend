from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import EmailMessage
from profiles.models import UsersPaidFeature, ProjectPaidFeature
import os
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_email(subject, body, to, attachments=None, count=0):
    logger.info(f'Task: Email sending to {to} started')
    if count == 10:
        return
    try:
        email = EmailMessage(
            subject,
            body,
            from_email=os.environ['EMAIL_HOST_USER'],
            to=[to]
        )
        if attachments:
            email.attach_file(attachments)
        email.send()
        logger.info(f'Task: Email sending to {to} finished')
    except Exception as e:
        logger.info(f'Task: Email sending to {to} failed {print(e) if count == 0 else ""}')
        send_email(subject, body, to, attachments, count=count+1)


@shared_task
def deactivate_user_feature(id):
    try:
        feature = UsersPaidFeature.objects.get(id=id)
        if feature.refresh_count == 0:
            feature.is_active = False
        else:
            feature.refresh_count -= 1
        feature.save()
    except:
        pass


@shared_task
def deactivate_project_feature(id):
    try:
        feature = ProjectPaidFeature.objects.get(id=id)
        if feature.refresh_count == 0:
            feature.is_active = False
        else:
            feature.refresh_count -= 1
        feature.save()
    except:
        pass
