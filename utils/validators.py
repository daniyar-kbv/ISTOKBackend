import os
import constants

from django.core.exceptions import ValidationError


def validate_file_size(value):
    if value.size > constants.MAX_REGULAR_FILE_SIZE:
        raise ValidationError(
            f'{constants.VALIDATION_MAX_FILE_SIZE}: {constants.MAX_REGULAR_FILE_SIZE}{constants.MB}'
        )


def basic_validate_images(value):
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in constants.IMAGE_EXTENSIONS:
        raise ValidationError(f'{constants.VALIDATION_NOT_ALLOWED_EXT}: {constants.IMAGE_EXTENSIONS}')
