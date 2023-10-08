from django.contrib.auth import hashers
from django.db.utils import IntegrityError
from django.test import TestCase
from ...models import User
from parameterized import parameterized


def field_provider():
    return [
        ("name", "Василий"),
        ("surname", "Петров"),
        ("email", "some-user@example.com"),
        ("phone", "+7-000-000-00-00"),
        ("is_locked", True),
        ("is_superuser", True),
        ("is_support", True),
        ("unix_group", "lihvou"),
        ("home_dir", "serik1987")
    ]


# noinspection PyUnresolvedReferences
class TestUser(TestCase):

    @parameterized.expand(["vanya", "stepan_090809890-udfiybvuf"])
    def test_positive(self, login):
        input_user = User(login=login)
        input_user.save()
        user = User.objects.get(id=input_user.id)
        self.assertEquals(user.login, login)
        for field in ["password_hash", "name", "surname", "email", "phone", "unix_group", "home_dir"]:
            self.assertIsNone(getattr(user, field))
        self.assertEquals(user.avatar.name, '')
        self.assertEquals(user.groups.count(), 0)
        self.assertEquals(User.objects.count(), 2)
        user.delete()
        self.assertEquals(User.objects.count(), 1)

    def test_user_name_null(self):
        with self.assertRaises(IntegrityError):
            User(login=None).save()

    def test_user_name_duplicated(self):
        with self.assertRaises(IntegrityError):
            for n in range(2):
                User(login="vasily").save()

    def test_other_fields_duplicated(self):
        for login in ["login1", "login2"]:
            User(login=login).save()

    @parameterized.expand(("password_hash", "activation_code_hash"))
    def test_set_credentials(self, field):
        credential = "some-secret-string"
        hashed = hashers.make_password(credential)
        user = User(login="vasya", **{field: hashed})
        user.save()
        user_copy = User.objects.get(id=user.id)
        recovered = getattr(user_copy, field)
        self.assertIsNotNone(recovered, "Password was not stored")
        self.assertTrue(hashers.check_password(credential, recovered), "Password storage is not reliable")

    @parameterized.expand(field_provider())
    def test_field(self, name, value):
        user = User(login="vasily")
        setattr(user, name, value)
        user.save()
        user_copy = User.objects.get(id=user.id)
        value_copy = getattr(user_copy, name)
        self.assertEquals(value_copy, value)
