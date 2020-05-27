import os, shutil


def user_avatar_path(instance, filename):
    return f'user_avatars/{instance.user.id}/{filename}'


def profile_document_path(instance, filename):
    return f'profile_documents/{instance.user.id}/{filename}'


def project_category_image_path(instance, filename):
    return f'project_category_images/{instance.id}/{filename}'


def delete_file(document):
    path = os.path.abspath(os.path.join(document.path, '..'))
    if os.path.isdir(path):
        shutil.rmtree(path)
