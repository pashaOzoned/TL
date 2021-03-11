import jwt

from datetime import datetime, timedelta

from django.conf import settings

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, email, lat, lng, password=None):
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email), lat=lat, lng=lng)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, lat, lng, password):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, lat, lng, password)
        user.is_superuser = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True)

    email = models.EmailField(db_index=True, unique=True)

    lat = models.FloatField(default=0.0)

    lng = models.FloatField(default=0.0)

    type_of_account = models.IntegerField(default=0)

    counter = models.IntegerField(default=0)

    time_last_change_location = models.DateTimeField(default=datetime.now())

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def token(self):
        return self._generate_jwt_token()

    def get_full_name(self):
        return self.username

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': '1646653442',
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')
