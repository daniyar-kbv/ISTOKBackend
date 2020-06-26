from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    name = 'main'
    verbose_name = 'Основной'

    def ready(self):
        import main.signals