from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import EmailMessage
from profiles.models import UsersPaidFeature, ProjectPaidFeature, Notification
from users.models import MainUser
from utils import general
import os
import logging, constants, requests

logger = logging.getLogger(__name__)


@shared_task
def send_sms(phone, code):
    headers = {
        'Content-Type': 'application/json',
        'Token': f'{os.environ.get("KAZINFO_SECRET_KEY")}'
    }
    data = {
        'phone': general.get_phone(phone),
        'type': 'sms',
        'msg': f'{constants.SMS_TEXT} {code}'
    }
    try:
        response = requests.post('http://isms.center/v1/validation/request', headers=headers, json=data)
        print(response.content)
    except requests.exceptions.ConnectionError:
        print('Connection refused')


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
            Notification.objects.create(text=f'Статус "PRO аккаунта" истек', user=feature.user)
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
            Notification.objects.create(text=f'Продвижение "{constants.PAID_FEATURE_TYPES[feature.type.type][1]}" проекта "{feature.project.name}" истекло',
                                        user=feature.project.user)
        else:
            feature.refresh_count -= 1
        feature.save()
    except:
        pass


@shared_task
def notify_user_feature(text, user_id):
    try:
        feature = UsersPaidFeature.objects.get(id=id)
        if feature.refresh_count == 0:
            Notification.objects.create(text=f'Статус "PRO аккаунта" истечет завтра', user=feature.user)
    except:
        pass


@shared_task
def notify_project_feature(id):
    try:
        feature = ProjectPaidFeature.objects.get(id=id)
        if feature.refresh_count == 0:
            Notification.objects.create(text=f'Продвижение "{constants.PAID_FEATURE_TYPES[feature.type.type][1]}" проекта "{feature.project.name}" истечет завтра',
                                        user=feature.project.user)
    except:
        pass
