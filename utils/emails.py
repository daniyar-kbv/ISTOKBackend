from utils import encryption
from users.views import UserViewSet

import constants


def generate_activation_email(email, request):
    return f"""
    {constants.ACTIVATION_EMAIL_BODY_START}
    {create_url(UserViewSet, 'verify-email', encryption.encrypt(email), request)}
    {constants.ACTIVATION_EMAIL_BODY_END}
    """


def create_url(viewset, name, arg, request):
    from users.urls import router
    view = viewset()
    view.basename = router.get_default_basename(UserViewSet)
    view.request = None
    base_url = request.build_absolute_uri("/")
    url = f'{base_url[0:len(base_url)-1]}{view.reverse_action(name, args=[arg])}'
    if url.__contains__('istokhome.ru'):
        url.replace('istokhome.ru', 'istokhome.com')
    if url.__contains__('istokhome.kz'):
        url.replace('istokhome.kz', 'istokhome.com')
    return url
