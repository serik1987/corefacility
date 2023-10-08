from parameterized import parameterized

from ....entity.user import User


class UserFieldMixin:
    """
    Contains common routines that check whether all user fields except password_hash and avatar were successfully loaded
    """

    @parameterized.expand([
        ("name",    "Василий"),
        ("name",    None),
        ("surname", "Иванов"),
        ("surname", None),
        ("email",   "vasily.ivanov@mail.ru"),
        ("email",   None),
        ("phone",   "+7 354 453 24 84"),
        ("phone",   None),
        ("is_locked", True),
        ("is_locked", False),
        ("is_superuser", True),
        ("is_superuser", False),
    ])
    def test_user_field(self, field_name, field_value):
        sample_user = User(login="sample_login")
        setattr(sample_user, field_name, field_value)
        sample_user.create()

        obj = self.get_entity_object_class()()
        obj.entity.user = sample_user
        obj.create_entity()
        obj.reload_entity()
        actual_field_value = getattr(obj.entity.user, field_name)
        self.assertEquals(actual_field_value, field_value,
                          "The field 'user.%s' was not retrieved successfully" % field_name)
