import os
import constants

from django.core.exceptions import ValidationError


# from utils.response import make_response


def validate_file_size(value):
    if value.size > constants.MAX_REGULAR_FILE_SIZE:
        raise ValidationError(
            f'{constants.VALIDATION_MAX_FILE_SIZE}: {constants.MAX_REGULAR_FILE_SIZE}{constants.MB}'
        )


# def validate_extension(value):
#     ext = os.path.splitext(value.name)[1]
#     if not ext.lower() in ALLOWED_EXTS:
#         raise ValidationError(f'not allowed file ext, allowed: {ALLOWED_EXTS}')

def basic_validate_images(value):
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in constants.IMAGE_EXTENSIONS:
        raise ValidationError(f'{constants.VALIDATION_NOT_ALLOWED_EXT}: {ALLOWED_EXTS}')

# def validate_password(password):
#     if not re.findall('\d', password):
#         raise serializers.ValidationError(make_response(messages=['The password must contain at least 1 digit, 0-9.']))
#     if len(password) < 8:
#         raise serializers.ValidationError(make_response(messages=['The password must be at least 8 symbols']))
