from django.db import models


class User(models.Model):
    """
    Defines the user information that will be stored in the database
    """
    login = models.SlugField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=256, null=True)
    name = models.CharField(max_length=100, null=True, db_index=True)
    surname = models.CharField(max_length=100, null=True, db_index=True)
    email = models.EmailField(null=True, unique=True)
    phone = models.CharField(max_length=20, null=True)
    is_locked = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_support = models.BooleanField(default=False)
    avatar = models.ImageField(null=True)
    unix_group = models.CharField(max_length=32, null=True, unique=True, editable=False)
    home_dir = models.CharField(max_length=100, null=True, unique=True, editable=False)
    activation_code_hash = models.CharField(max_length=256, null=True, editable=False)
    activation_code_expiry_date = models.DateTimeField(null=True, editable=False)
