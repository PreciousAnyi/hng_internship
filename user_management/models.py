from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, firstName, lastName, password=None, phone=None):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, firstName=firstName, lastName=lastName, phone=phone)
        user.set_password(password)
        user.userId = uuid.uuid4()
        user.date_joined = timezone.now()  # Ensure date_joined is set
        user.save(using=self._db)
        return user

    def create_superuser(self, email, firstName, lastName, password, phone=None):
        user = self.create_user(email=email, firstName=firstName, lastName=lastName, password=password, phone=phone)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    userId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firstName = models.CharField(max_length=255, null=False)
    lastName = models.CharField(max_length=255, null=False)
    email = models.EmailField(unique=True, null=False)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    last_login = models.DateTimeField(default=timezone.now)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstName', 'lastName']

    def __str__(self):
        return self.email

class Organization(models.Model):
    orgId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User, related_name='organizations')

    def __str__(self):
        return self.name