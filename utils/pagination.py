from rest_framework.response import Response
from rest_framework import pagination, status


class CustomPagination(pagination.PageNumberPagination):
    page_size = 5

    def get_paginated_response(self, data, additional_data=None):
        print(additional_data)
        data = {
            'results': data,
            'additional_data': additional_data,
            'page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
        }
        print(data)
        return Response(data, status=status.HTTP_200_OK)
