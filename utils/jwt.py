from rest_framework_jwt.compat import get_username_field, get_username
from rest_framework_jwt.settings import api_settings
from calendar import timegm
from datetime import datetime
from users.models import MerchantPhone
import uuid, warnings, time


def jwt_payload_handler(user):
    username_field = get_username_field()
    username = get_username(user)

    warnings.warn(
        'The following fields will be removed in the future: '
        '`email` and `user_id`. ',
        DeprecationWarning
    )

    payload = {
        'user_id': user.pk,
        'username': username,
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
    }
    if hasattr(user, 'email'):
        payload['email'] = user.email
    if isinstance(user.pk, uuid.UUID):
        payload['user_id'] = str(user.pk)
    if hasattr(user, 'role'):
        payload['role'] = user.role
    if user.profile:
        payload['first_name'] = user.profile.first_name
        payload['last_name'] = user.profile.last_name
    phones = []
    for p in MerchantPhone.objects.filter(user=user):
        phones.append(p.phone)
    payload['phones'] = phones


    payload[username_field] = username

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload