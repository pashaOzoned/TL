from django.db import models
from authentication.models import User


class Photo(models.Model):
    user_id = models.IntegerField(default=1)
    url = models.CharField(max_length=300)
    title = models.CharField(max_length=300)

    def __str__(self):
        return self.url
