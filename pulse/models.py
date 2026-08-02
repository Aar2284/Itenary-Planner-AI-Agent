from django.db import models


class AnomalyEvent(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    sensor_reading = models.FloatField()
    severity_score = models.IntegerField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Anomaly at {self.timestamp} - {self.sensor_reading}°C"
