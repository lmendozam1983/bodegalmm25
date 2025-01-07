from django.apps import AppConfig


class DispositivosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dispositivo'
    verbose_name = 'Dispositivos'
    
    def ready(self):
        import dispositivo.signals
