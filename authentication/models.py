from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):

    can_be_contacted = models.BooleanField(default=True, null=False)
    can_data_be_shared = models.BooleanField(default=True, null=False)
    date_of_birth = models.DateField(blank=False, null=False)

    def __str__(self):
        return self.username
