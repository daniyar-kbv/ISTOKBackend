from django.apps import AppConfig


class OtherConfig(AppConfig):
    name = 'other'

    def ready(self):
        import other.signals