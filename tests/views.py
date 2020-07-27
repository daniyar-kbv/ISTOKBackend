from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from tests.serializers import ProjectCreateSerializer, BlogPostCreateSerializer, MerchantReviewCreateSerialzier, \
    MerchantReviewReplyCreateSerializer, ProjectCommentCreateSerialzier, ProjectCommentReplyCreateSerializer
from main.models import Project, ProjectComment, ProjectCommentReply
from blog.models import BlogPost
from users.models import MerchantReview, ReviewReply
from utils import general, auth
import requests, os, json


class ProjectViewSet(viewsets.GenericViewSet,
                     mixins.CreateModelMixin):
    serializer_class = ProjectCreateSerializer
    queryset = Project.objects.all()

    def create(self, request, *args, **kwargs):
        documents = request.data.getlist('documents')
        context = {
            'documents': documents
        }
        serializer = ProjectCreateSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get', 'post'], authentication_classes=[auth.CsrfExemptSessionAuthentication, ])
    def tests(self, request, pk=None):
        print(request.method)
        print(request.headers)
        print(request.data)
        credentials = general.encode_base64(
            # f'{os.environ.get("PAYMENTS_PUBLIC_ID")}:{os.environ.get("PAYMENTS_API_SECRET")}'
            f'{"pk_b826aa0af00e5286511d54e746fda"}:{"c40a0ba72b7ed318e713d71cb9153204"}'
        )
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json'
        }
        data = {
            "Amount": 1000,
            "Currency": "KZT",
            "Name": "NAME NAME",
            "CardCryptogramPacket": request.data.get('packet'),
            "InvoiceId": "123123",
            "Email": "daniyarkurmanbayev123@gmail.com"
        }
        response = requests.post('https://api.cloudpayments.ru/payments/cards/charge', headers=headers, json=data)
        res_data = response.json()
        model = res_data.get('Model')
        if model:
            acs_url = model.get('AcsUrl')
            transaction_id = model.get('TransactionId')
            pa_req = model.get('PaReq')
            if acs_url and transaction_id and pa_req:
                context = {
                    'acs_url': acs_url,
                    'transaction_id': transaction_id,
                    'pa_req': pa_req
                }
                return render(request, '3ds.html', context=context)
        return Response(response.json())

    @action(detail=False, methods=['get', 'post'])
    def pay_template(self, request, pk=None):
        return render(request, 'pay_template.html')

    @action(detail=False, methods=['get', 'post'])
    def pay_template_test(self, request, pk=None):
        context = {
            'pay_url': request.build_absolute_uri(reverse('features'))
        }
        return render(request, 'pay_template_prod.html', context=context)

    @action(detail=False, methods=['get', 'post'])
    def secure(self, request, pk=None):
        return render(request, '3ds.html')

    @action(detail=False, methods=['get', 'post'])
    def result_page(self, request, pk=None):
        return render(request, 'result_page.html')

    @action(detail=False, methods=['get', 'post'], authentication_classes=[auth.CsrfExemptSessionAuthentication, ])
    def secure_term(self, request, pk=None):
        print(request.method)
        credentials = general.encode_base64(
            # f'{os.environ.get("PAYMENTS_PUBLIC_ID")}:{os.environ.get("PAYMENTS_API_SECRET")}'
            f'{"pk_b826aa0af00e5286511d54e746fda"}:{"c40a0ba72b7ed318e713d71cb9153204"}'
        )
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json'
        }
        data = {
            'TransactionId': request.data.get('MD'),
            'PaRes': request.data.get('PaRes')
        }
        response = requests.post('https://api.cloudpayments.ru/payments/cards/post3ds', headers=headers, json=data)
        print(response.content)
        return redirect('http://0.0.0.0:8990/api/tests/projects/pay_template/')

    @action(detail=False, methods=['get', 'post'], authentication_classes=[auth.CsrfExemptSessionAuthentication, ])
    def tests2(self, request, pk=None):
        return Response(request.build_absolute_uri(reverse('test_auth')))

    @action(detail=False, methods=['get'], authentication_classes=[auth.CsrfExemptSessionAuthentication, ])
    def test_cities(self, request, pk=None):
        import random
        cities = ['Абай', 'Акколь', 'Аксай', 'Аксу', 'Актау', 'Актобе', 'Алга', 'Алматы', 'Арал', 'Аркалык', 'Аркалык', 'Арыс', 'Астана', 'Атбасар', 'Атырау', 'Аягоз', 'Байконур', 'Балхаш', 'Булаево', 'Державинск', 'Ерейментау', 'Есик', 'Есиль', 'Жанаозен', 'Жанатас', 'Жаркент', 'Жезказган', 'Жем', 'Жетысай', 'Житикара', 'Зайсан', 'Зыряновск', 'Капшагай', 'Караганды', 'Кокшетау', 'Костанай', 'Кызылорда', 'Ленгер', 'Лисаковск', 'Макинск', 'Павлодар', 'Петропавловск', 'Риддер', 'Рудный', 'Сатпаев', 'Степногорск', 'Талгар', 'Талдыкорган', 'Тараз', 'Уральск', 'Усть-Каменогорск', 'Хромтау', 'Шемонаиха', 'Шымкент', 'Щучинск', 'Экибастуз']
        char = ''
        url = '/api/media/test_cities/' + random.choice(['clowdy.png', 'clowdy2.png', 'sunny.png', 'rain.png'])
        abs_uri = request.build_absolute_uri(url)
        if request.GET.get('char'):
            char = request.GET.get('char')
        data = {
            'cities': [city for city in cities if city[0].lower() == char.lower() or char == ''],
            'img': abs_uri
        }
        return Response(data)


class BlogPostViewSet(viewsets.GenericViewSet,
                      mixins.CreateModelMixin):
    queryset = BlogPost.objects.all()

    def create(self, request, *args, **kwargs):
        documents = request.data.getlist('documents')
        context = {
            'documents': documents
        }
        serializer = BlogPostCreateSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MerchantReviewViewSet(viewsets.GenericViewSet,
                            mixins.CreateModelMixin):
    queryset = MerchantReview.objects.all()

    def create(self, request, *args, **kwargs):
        documents = request.data.getlist('documents')
        context = {
            'documents': documents
        }
        serializer = MerchantReviewCreateSerialzier(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MerchantReviewReplyViewSet(viewsets.GenericViewSet,
                                 mixins.CreateModelMixin):
    queryset = ReviewReply.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            review = MerchantReview.objects.get(id=request.data.get('review'))
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            ReviewReply.objects.get(review=review)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            pass
        data = request.data
        data['user'] = review.merchant_id
        serializer = MerchantReviewReplyCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProjectCommentViewSet(viewsets.GenericViewSet,
                            mixins.CreateModelMixin):
    queryset = ProjectComment.objects.all()

    def create(self, request, *args, **kwargs):
        documents = request.data.getlist('documents')
        context = {
            'documents': documents
        }
        serializer = ProjectCommentCreateSerialzier(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProjectCommentReplyViewSet(viewsets.GenericViewSet,
                                 mixins.CreateModelMixin):
    queryset = ProjectCommentReply.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            comment = ProjectComment.objects.get(id=request.data.get('comment'))
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            ProjectCommentReply.objects.get(comment=comment)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            pass
        data = request.data
        data._mutable = True
        data['user'] = comment.project.user_id
        serializer = ProjectCommentReplyCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


