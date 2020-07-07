from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.response import Response
from rest_framework import status
from users.models import MainUser
from main.models import Project
from payments.models import Transaction, UsersPaidFeature, ProjectPaidFeature, \
    ProjectLinkedPaidFeatures, PaidFeatureType
from main.tasks import deactivate_project_feature, deactivate_user_feature, notify_user_feature, notify_project_feature
from utils import general
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import requests, constants, os


def make_payment(type, request, instance, target):
    if isinstance(instance, MainUser):
        name = instance.get_full_name()
        email = instance.email
        user = instance
        project = None
    else:
        name = instance.user.get_full_name()
        email = instance.user.email
        user = instance.user
        project = instance
    if type.type == constants.PAID_FEATURE_PRO:
        transaction_type = constants.PAID_FEATURE_FOR_USER
    else:
        transaction_type = constants.PAID_FEATURE_FOR_PROJECT
    transaction = Transaction.objects.create(feature_type=type,
                                             type=transaction_type,
                                             user=user,
                                             project=project,
                                             sum=type.price)
    data = {
        "Amount": type.price,
        "Currency": "KZT",
        "Name": name,
        "CardCryptogramPacket": request.data.get('packet'),
        "InvoiceId": transaction.id,
        "Email": email
    }
    response = make_request(constants.PAYMENT_REQUEST_PAYMENT, data=data)
    res_data = response.json()
    success = res_data.get('Success')
    model = res_data.get('Model')
    if success:
        make_features(type, instance, transaction)
        #     TODO: success url
        model = res_data.get('Model')
        message = model.get('CardHolderMessage')
        return redirect(f'{request.build_absolute_uri(reverse("result_page"))}?message={message}')
    else:
        if model:
            acs_url = model.get('AcsUrl')
            transaction_id = model.get('TransactionId')
            pa_req = model.get('PaReq')
            message = model.get('CardHolderMessage')
            if acs_url and transaction_id and pa_req:
                context = {
                    'acs_url': acs_url,
                    'transaction_id': transaction_id,
                    'pa_req': pa_req,
                    'term_url': f'{request.build_absolute_uri(reverse("3ds"))}?transaction_id={transaction.id}&target={target}&instance_id={instance.id}&feature_id={type.id}'
                }
                return render(request, '3ds_prod.html', context=context)
            elif message:
                # TODO: failure url
                return redirect(f'{request.build_absolute_uri(reverse("result_page"))}?message={message}')
        return redirect(request.build_absolute_uri(reverse("result_page")))


def confirm_3ds(request):
    data = {
        'TransactionId': request.data.get('MD'),
        'PaRes': request.data.get('PaRes')
    }
    response = make_request(constants.PAYMENT_REQUEST_3DS, data).json()
    success = response.get('Success')
    if success:
        if int(request.GET.get('target')) == constants.PAID_FEATURE_FOR_USER:
            instance = MainUser.objects.get(id=int(request.GET.get('instance_id')))
        else:
            instance = Project.objects.get(id=int(request.GET.get('instance_id')))
        transaction = Transaction.objects.get(id=int(request.GET.get('transaction_id')))
        type = PaidFeatureType.objects.get(id=int(request.GET.get('feature_id')))
        make_features(type, instance, transaction)
        # TODO: success url
        model = response.get('Model')
        message = model.get('CardHolderMessage')
        return redirect(f'{request.build_absolute_uri(reverse("result_page"))}?message={message}')
    else:
        model = response.get('Model')
        if model:
            message = model.get('CardHolderMessage')
            if message:
                # TODO: failure url
                return redirect(f'{request.build_absolute_uri(reverse("result_page"))}?message={message}')
        # TODO: failure url
        return redirect(request.build_absolute_uri(reverse("result_page")))


def make_request(type, data):
    credentials = general.encode_base64(
        f'{os.environ.get("PAYMENTS_PUBLIC_ID")}:{os.environ.get("PAYMENTS_API_SECRET")}'
    )
    headers = {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/json'
    }
    if type == constants.PAYMENT_REQUEST_PAYMENT:
        url = constants.PAYMENT_REQUEST_URL
    elif type == constants.PAYMENT_REQUEST_3DS:
        url = constants.PAYMENT_REQUEST_3DS_URL
    return requests.post(url, headers=headers, json=data)


def create_feature(type, instance, transaction, is_main=True):
    if type.type == constants.PAID_FEATURE_PRO:
        features = UsersPaidFeature.objects.filter(user=instance, is_active=True)
    else:
        features = ProjectPaidFeature.objects.filter(project=instance, type=type, is_active=True)
    if features.count() > 0:
        feature = features.first()
        unit = feature.type.time_unit
        amount = feature.type.time_amount
        if unit == constants.TIME_DAY:
            delta = timedelta(days=amount)
        elif unit == constants.TIME_MONTH:
            delta = relativedelta(months=+amount)
        elif unit == constants.TIME_YEAR:
            delta = relativedelta(years=+amount)
        else:
            delta = timedelta(seconds=10)
        feature.expires_at = feature.expires_at + delta
        feature.refresh_count += 1
        feature.save()
    else:
        if type.type == constants.PAID_FEATURE_PRO:
            feature = UsersPaidFeature.objects.create(user=instance, type=type, is_active=True)
        else:
            feature = ProjectPaidFeature.objects.create(project=instance, type=type, is_active=True)
    if type.type == constants.PAID_FEATURE_PRO:
        notify_user_feature.apply_async(args=[feature.id], eta=(feature.expires_at - timedelta(days=1)))
        deactivate_user_feature.apply_async(args=[feature.id], eta=feature.expires_at)
    else:
        notify_project_feature.apply_async(args=[feature.id], eta=(feature.expires_at - timedelta(days=1)))
        deactivate_project_feature.apply_async(args=[feature.id], eta=feature.expires_at)
    if is_main:
        if type.type == constants.PAID_FEATURE_PRO:
            transaction.user_feature = feature
        else:
            transaction.project_feature_main = feature
    else:
        transaction.project_feature_secondary = feature
    transaction.succeeded = True
    transaction.save()


def make_features(type, instance, transaction):
    if type.type != constants.PAID_FEATURE_TOP_DETAILED:
        create_feature(type, instance, transaction)
    else:
        main_feature = ProjectLinkedPaidFeatures.objects.get(main_feature=type)
        create_feature(main_feature.first_feature, instance, transaction)
        create_feature(main_feature.second_feature, instance, transaction, False)
