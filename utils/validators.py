import os
import constants, re
from django.core.exceptions import ValidationError
# from payments.models import PaidFeatureType
from utils import response


def validate_file_size(value):
    if value.size > constants.MAX_REGULAR_FILE_SIZE:
        raise ValidationError(
            f'{constants.VALIDATION_MAX_FILE_SIZE}: {constants.MAX_REGULAR_FILE_SIZE}{constants.MB}'
        )


def basic_validate_images(value):
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in constants.IMAGE_EXTENSIONS:
        raise ValidationError(f'{constants.VALIDATION_NOT_ALLOWED_EXT}: {constants.IMAGE_EXTENSIONS}')


def validate_password(password):
    if len(password) < 8:
        raise ValidationError(constants.VALIDATION_PASSWORD_LENGTH)
    if not re.findall('\d', password):
        raise ValidationError(constants.VALIDATION_PASSWORD_DIGITS)
    if not re.findall('[A-Z]', password):
        raise ValidationError(constants.VALIDATION_PASSWORD_UPPERCASE)
    if not re.findall('[a-z]', password):
        raise ValidationError(constants.VALIDATION_PASSWORD_LOWERCASE)
    return password


def validate_phone(value):
    regex = constants.PHONE_FORMAT
    if not isinstance(value, str) or re.search(regex, value) is None:
        raise ValidationError(constants.VALIDATION_PHONE_FORMAT_ERROR)
    return value

