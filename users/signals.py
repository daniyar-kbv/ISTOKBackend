from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from users.models import UserActivation, MainUser, ProfileDocument, ProjectCategory, MerchantReview, ClientRating, \
    ReviewDocument, ReviewReply, ReviewReplyDocument, CodeVerification
from main.models import Subscriber
from main.tasks import send_email, send_sms
from utils import emails, upload
import constants


@receiver(post_save, sender=UserActivation)
def activation_created(sender, instance, created=True, **kwargs):
    if instance:
        attrs_needed = ['_request', '_created']
        if all(hasattr(instance, attr) for attr in attrs_needed):
            if instance._created:
                send_email.delay(constants.ACTIVATION_EMAIL_SUBJECT,
                                 emails.generate_activation_email(instance.email, request=instance._request),
                                 instance.email)

@receiver(post_save, sender=MainUser)
def user_post_save(sender, instance, created=True, **kwargs):
    if created:
        Subscriber.objects.create(email=instance.email)

@receiver(pre_delete, sender=MainUser)
def user_pre_delete(sender, instance, created=True, **kwargs):
    if instance.profile:
        if instance.profile.avatar:
            upload.delete_folder(instance.profile.avatar)
    doc = ProfileDocument.objects.filter(user=instance).first()
    if doc:
        upload.delete_folder(doc.document)


@receiver(pre_delete, sender=ProfileDocument)
def profile_document_pre_delete(sender, instance, created=True, **kwargs):
    if instance.document:
        upload.delete_file(instance.document)


@receiver(pre_delete, sender=ProjectCategory)
def category_pre_delete(sender, instance, created=True, **kwargs):
    upload.delete_file(instance.image)


@receiver(post_save, sender=MerchantReview)
def merchant_review_post_save(sender, instance, created=True, **kwargs):
    if created:
        rating_sum = 0
        rating_count = 0
        merchant = instance.merchant
        reviews = MerchantReview.objects.filter(merchant=merchant)
        for review in reviews:
            rating_count += 1
            rating_sum += review.rating
        profile = merchant.profile
        profile.rating = rating_sum/rating_count
        profile.save()


@receiver(pre_delete, sender=MerchantReview)
def merchant_review_pre_delete(sender, instance, created=True, **kwargs):
    doc = ReviewDocument.objects.filter(review=instance).first()
    if doc:
        upload.delete_folder(doc.document)
    rating_sum = 0
    rating_count = 0
    merchant = instance.merchant
    reviews = MerchantReview.objects.filter(merchant=merchant)
    for review in reviews:
        rating_count += 1
        rating_sum += review.rating
    profile = merchant.profile
    profile.rating = rating_sum / rating_count
    profile.save()


@receiver(post_save, sender=ClientRating)
def client_rating_post_save(sender, instance, created=True, **kwargs):
    if created:
        rating_sum = 0
        rating_count = 0
        client = instance.client
        ratings = ClientRating.objects.filter(client=client)
        for rating in ratings:
            rating_count += 1
            rating_sum += rating.rating
        profile = client.profile
        profile.rating = rating_sum / rating_count
        profile.save()


@receiver(pre_delete, sender=ClientRating)
def client_rating_pre_delete(sender, instance, created=True, **kwargs):
    rating_sum = 0
    rating_count = 0
    client = instance.client
    ratings = ClientRating.objects.filter(client=client)
    for rating in ratings:
        rating_count += 1
        rating_sum += rating.rating
    profile = client.profile
    profile.rating = rating_sum / rating_count
    profile.save()


@receiver(pre_delete, sender=ReviewReply)
def review_reply_pre_delete(sender, instance, created=True, **kwargs):
    doc = ReviewReplyDocument.objects.filter(reply=instance).first()
    if doc:
        upload.delete_folder(doc.document)


# @receiver(post_save, sender=CodeVerification)
# def code_verification_saved(sender, instance, created=True, **kwargs):
#     if created:
        # send_sms.delay(instance.phone.phone, instance.code)
