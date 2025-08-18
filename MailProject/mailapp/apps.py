from django.apps import AppConfig


class MailappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailapp'
    
    def ready(self):
        import mailapp.signals
