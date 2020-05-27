from rest_framework.views import exception_handler
from django.http import Http404


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, Http404):
        print(context.get('view').serializer_class)
        custom_response_data = {
            'messages': ['Object does not exist']
        }
        response.data = custom_response_data # set the custom response data on response object

    return response
