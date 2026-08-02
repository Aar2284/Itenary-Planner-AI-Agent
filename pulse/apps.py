from django.apps import AppConfig


class PulseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pulse'

    def ready(self):
        from pulse.ml_brain import train_model
        train_model()
