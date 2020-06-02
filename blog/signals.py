from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from blog.models import MainPageBlogPost


@receiver(post_save, sender=MainPageBlogPost)
def main_page_post_created(sender, instance, created, **kwargs):
    if instance and created:
        post = instance.post
        post.is_main = True
        post.save()


@receiver(pre_delete, sender=MainPageBlogPost)
def main_page_pre_delete(sender, instance, **kwargs):
    if instance:
        post = instance.post
        post.is_main = False
        post.save()

