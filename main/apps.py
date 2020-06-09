from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    name = 'main'

    def ready(self):
        import main.signals