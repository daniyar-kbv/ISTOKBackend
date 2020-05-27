from rest_framework.response import Response
from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    page_size = 20

    def get_paginated_response(self, data):
        data_in_data = data.pop('data')
        data['data'] = {
            'results': data_in_data,
            'page': self.page.number,
            'totalPages': self.page.paginator.num_pages
        }
        return Response(data)