from django.apps import AppConfig


class Festival2026Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Festival2026'

    def ready(self):
        # Conecta las signals al iniciar la app
        # Esto hace que SignalCorreoCliente se dispare
        # automáticamente con cada reservación nueva
        import Festival2026.signals  # noqa: F401