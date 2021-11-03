from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    name = 'payments'
    verbose_name = 'Платные услуги'

    def ready(self):
        import payments.signals
