from django.apps import AppConfig


class AlgebraConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    # Ruta completa del paquete de la app (está dentro de "apps/algebra")
    name = "apps.algebra"
