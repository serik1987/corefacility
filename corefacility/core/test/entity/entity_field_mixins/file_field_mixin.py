import os

from django.conf import settings


class FileFieldMixin:
    """
    Use this mixin to test file fields.

    The sample way to test a single file field:
    @parameterized.expand(image_provider())
    def test_avatar_default(self, image_path, throwing_exception, test_number):
        self._test_file_field("avatar", "/static/core/science.svg", ImageFile,
                              image_path, throwing_exception, test_number)
    """

    FILE_TEST_DEFAULT = 0
    FILE_TEST_UPLOAD = 1
    FILE_TEST_UPLOAD_AND_DELETE = 2
    FILE_TEST_UPLOAD_TWO_FILES_TWO_PROJECTS = 3
    FILE_TEST_UPLOAD_TWO_FILES_SAME_PROJECT = 4

    def _test_file_field(self, field_name, default_url, file_wrapper_class,
                         full_path, throwing_exception, route_number):
        """
        Tests the file upload and delete

        :param field_name: the field name corresponding to the file
        :param default_url: the default URL that must be shown when the file has not been loaded
        :param file_wrapper_class: the django.core.files.File subclass that will be used to induce file to the model
        :param full_path: the full file path
        :param throwing_exception: exception to throw is the file is invalid, None for positive tests
        :param route_number: 0 - just check the default field value, 1 - upload the file and check,
            2 - download the file and check
        :return: nothing
        """
        obj = self.get_entity_object_class()()
        obj.create_entity()
        file_field = getattr(obj.entity, field_name)
        if route_number == self.FILE_TEST_DEFAULT:
            self.assertEquals(file_field.url, default_url,
                              "The default file URL is not the same as expected when the entity is created")
            obj.reload_entity()
            self.assertEquals(file_field.url, default_url,
                              "The default file URL is not the same as expected when the entity is loaded")
            self.assertTrue(file_field.url.startswith("/static/"),
                            "The default file is not a static file")
            return

        file_object = open(full_path, "rb")
        django_file = file_wrapper_class(file_object)
        file_field.attach_file(django_file)
        url_upon_create = file_field.url
        if route_number == self.FILE_TEST_UPLOAD:
            self.assertTrue(url_upon_create.startswith("/media/"),
                            "The uploaded files must be stored in the media folder")
            self.assertMediaRootFiles(1,
                                      "We have uploaded our first file but total number of files in the media root "
                                      "is not one")

        obj.reload_entity()
        file_field = getattr(obj.entity, field_name)
        url = file_field.url
        if route_number == self.FILE_TEST_UPLOAD:
            self.assertTrue(url.startswith("/media/"),
                            "The uploaded files must be stored in the media folder")
            self.assertEquals(url_upon_create, url, "Unable to compute the URL of the uploaded file")

        if route_number == self.FILE_TEST_UPLOAD_AND_DELETE:
            file_field.detach_file()
            self.assertMediaRootFiles(0, "The file has already detached but still present in the media folder")
            self.assertEquals(file_field.url, default_url,
                              "The URL was not recovered to the default one after file detachment")
            obj.reload_entity()
            file_field = getattr(obj.entity, field_name)
            self.assertEquals(file_field.url, default_url,
                              "The file detachment was not provided in the database")

        if route_number == self.FILE_TEST_UPLOAD_TWO_FILES_TWO_PROJECTS:
            obj2 = self.get_entity_object_class()()
            obj2.change_entity_fields()
            obj2.create_entity()
            file_field2 = getattr(obj2.entity, field_name)
            file_field2.attach_file(django_file)
            self.assertMediaRootFiles(2,
                                      "Two files attached to two entities, two files shall be contained in the "
                                      "media root folder, but this is not true")
            self.assertNotEqual(file_field.url, file_field2.url,
                                "Two files attached to two entities have the same URL")

        if route_number == self.FILE_TEST_UPLOAD_TWO_FILES_SAME_PROJECT:
            file_field.attach_file(django_file)
            self.assertMediaRootFiles(1, "When another file is attached to the project the previous one shall be "
                                         "detached and deleted from the media root. This was not happened")

    def assertMediaRootFiles(self, n, msg):
        """
        Asserts the media root folder contains certain media files

        :param n: number of media files that shall be contained in the media root
        :param msg: message to show if this is not true
        :return: nothing
        """
        root = settings.MEDIA_ROOT
        file_number = 0
        for filename in os.listdir(root):
            fullname = os.path.join(root, filename)
            if os.path.isfile(fullname):
                file_number += 1

        self.assertEquals(file_number, n, msg)
