from django.db.models.deletion import RestrictedError
from django.db.utils import IntegrityError
from django.test import TestCase
from parameterized import parameterized

from ...models import Module, EntryPoint


class TestAppIntegrity(TestCase):

    def test_application_delete(self):
        # noinspection PyUnresolvedReferences
        core_module = Module.objects.get(parent_entry_point=None, alias="core")
        with self.assertRaises(RestrictedError):
            core_module.delete()

    @parameterized.expand([
        ("authorizations", False),
        ("processors", True)
    ])
    def test_app_alias_uniqueness(self, ep_alias, exceptions):
        # noinspection PyUnresolvedReferences
        module = Module(
            alias="roi",
            parent_entry_point=EntryPoint.objects.get(alias=ep_alias),
            name="Some module",
            user_settings={})
        if exceptions:
            with self.assertRaises(IntegrityError):
                module.save()
        else:
            module.save()

    @parameterized.expand([
        ("authorizations", True),
        ("processors", False)
    ])
    def test_ep_alias_uniqueness(self, ep_alias, exceptions):
        # noinspection PyUnresolvedReferences
        ep = EntryPoint(
            alias=ep_alias,
            belonging_module=Module.objects.get(alias="core"),
            name="Some entry point",
            type="lst"
        )
        if exceptions:
            with self.assertRaises(IntegrityError):
                ep.save()
        else:
            ep.save()
