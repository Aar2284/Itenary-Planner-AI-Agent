from django.contrib import admin
from .models import AnomalyEvent


@admin.register(AnomalyEvent)
class AnomalyEventAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'sensor_reading', 'severity_score')
    list_filter = ('severity_score',)
    ordering = ('-timestamp',)
