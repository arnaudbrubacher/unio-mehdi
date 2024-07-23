from django.apps import AppConfig

class Vt1500AdminConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "vt1500admin"

    def ready(self):
        pass