from django.db.models.signals import post_save
from django.dispatch import receiver
from other.models import MailingRecipient, Mailing
from main.tasks import send_email
import constants


@receiver(post_save, sender=Mailing)
def mailing_created(sender, instance, created=True, **kwargs):
    emails = MailingRecipient.objects.filter(is_subscribed=True).values_list('email', flat=True)
    if created:
        for email in emails:
            print(email)
            #send_email.delay(instance.title, instance.text, email)
