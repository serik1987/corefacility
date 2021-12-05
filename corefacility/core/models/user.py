from django.db import models


class User(models.Model):
    """
    Defines the user information that will be stored in the database
    """
    login = models.SlugField(max_length=100, unique=True,
                             help_text="the user login")
    password_hash = models.CharField(max_length=256, null=True,
                                     help_text="The password hash for simple login procedure or None if simple login "
                                               "procedure is not available for this user")
    name = models.CharField(max_length=100, null=True,
                            help_text="User first name")
    surname = models.CharField(max_length=100, null=True,
                               help_text="User last name")
    email = models.EmailField(null=True, unique=True,
                              help_text="E-mail that will be used for receiving notifications")
    phone = models.CharField(max_length=20, null=True,
                             help_text="The user phone for connections via What's App etc.")
    is_locked = models.BooleanField(help_text="True if the user is unable to login in any way")
    is_superuser = models.BooleanField(help_text="True, if the user has all possible permissions")
    is_support = models.BooleanField(help_text="True oif the user is technical support")
    avatar = models.ImageField(null=True,
                               help_text="User photo or another picture")
    unix_group = models.CharField(max_length=32, null=True, unique=True, editable=False,
                                  help_text="The UNIX group belonging to the user")
    home_dir = models.CharField(max_length=100, null=True, unique=True, editable=False,
                                help_text="The home directory belonging to the user")
    activation_code_hash = models.CharField(max_length=256, null=True, editable=False,
                                            help_text="The activation code hash for password recovery via E-mail or "
                                                      "None if activation code has not sent yet")
    activation_code_expiry_date = models.DateTimeField(null=True, editable=False,
                                                       help_text="The activation code when given is valid until this "
                                                                 "date")
