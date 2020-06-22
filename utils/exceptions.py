from rest_framework.views import exception_handler
from django.http import Http404


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if hasattr(exc, 'detail'):
        custom_response_data = {
            'messages': [exc.detail]
        }
        response.data = custom_response_data

    return response
