from __future__ import absolute_import, unicode_literals

from celery import shared_task

from django.core.mail import EmailMessage

import os
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_email(subject, body, to, attachments=None, count=0):
    logger.info(f'Task: Email sending to {to} started')
    if count == 10:
        return
    # try:
    email = EmailMessage(
        subject,
        body,
        from_email=os.environ['EMAIL_HOST_USER'],
        to=[to]
    )

    print(email.subject)
    print(email.body)
    print(email.from_email)
    print(email.to)
    if attachments:
        print('asd')
        email.attach_file(attachments)
    email.send()
    logger.info(f'Task: Email sending to {to} finished')
    # except:
    #     logger.info(f'Task: Email sending to {to} failed')
    #     send_email(subject, body, to, attachments, count=count+1)
