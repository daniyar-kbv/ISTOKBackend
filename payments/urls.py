from django.urls import path
from payments.views import PaidFeaturesAPIView, AuthAPIView, SecureAPIView, ResultPageAPIView
from rest_framework import routers


urlpatterns = [
    path('features/', PaidFeaturesAPIView.as_view(), name='features'),
    path('features/<int:pk>/', PaidFeaturesAPIView.as_view(), name='features_pk'),
    path('3ds/', SecureAPIView.as_view(), name='3ds'),
    path('auth/', AuthAPIView.as_view(), name='test_auth'),
    path('result_page/', ResultPageAPIView.as_view(), name='result_page')
]
