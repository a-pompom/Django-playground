from django.db import models


class Sample(models.Model):
    text = models.CharField(max_length=255)
