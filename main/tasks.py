from __future__ import absolute_import, unicode_literals

from celery import shared_task

from django.core.mail import EmailMessage

import os
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_email(subject, body, to, attachments=None):
    logger.info(f'Task: Email sending to {to} started')
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
    except:
        logger.info(f'Task: Email sending to {to} failed')
        send_email(subject, body, to, attachments)
