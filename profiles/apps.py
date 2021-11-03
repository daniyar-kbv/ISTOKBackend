from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    name = 'profiles'
    verbose_name = 'Профиль'

    def ready(self):
        import profiles.signals