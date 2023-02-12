from django.db import models

# Create your models here.
class Geo(models.Model):
    lat = models.BigIntegerField()
    lon = models.BigIntegerField()
    w = models.PositiveBigIntegerField()
    h = models.PositiveBigIntegerField()