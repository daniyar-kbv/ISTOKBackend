import os, shutil


def user_avatar_path(instance, filename):
    return f'user_avatars/{instance.user.id}/{filename}'


def profile_document_path(instance, filename):
    return f'profile_documents/{instance.user.id}/{filename}'


def review_document_path(instance, filename):
    return f'review_documents/{instance.review.id}/{filename}'


def project_category_image_path(instance, filename):
    return f'project_category_images/{filename}'


def blog_post_document_path(instance, filename):
    return f'blog_post_documents/{instance.post.id}/{filename}'


def project_document_path(instance, filename):
    return f'project_documents/{instance.project.id}/{filename}'


def project_render360_path(instance, filename):
    return f'project_render360_documents/{instance.project.id}/{filename}'


def project_comment_document_path(instance, filename):
    return f'project_comment_documents/{instance.comment.id}/{filename}'


def delete_folder(document):
    path = os.path.abspath(os.path.join(document.path, '..'))
    if os.path.isdir(path):
        shutil.rmtree(path)


def delete_file(document):
    path = os.path.abspath(os.path.join(document.path, '.'))
    if os.path.isdir(path):
        shutil.rmtree(path)
