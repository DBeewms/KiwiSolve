from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    # Ruta completa del paquete de la app (está dentro de "apps/pages")
    name = "apps.pages"
