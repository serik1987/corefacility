import os
import pathlib

from core.test.entity.entity_field_mixins.file_field_mixin import FileFieldMixin

USEFUL_TEST_CASES = {FileFieldMixin.FILE_TEST_UPLOAD,
                     FileFieldMixin.FILE_TEST_UPLOAD_AND_DELETE,
                     FileFieldMixin.FILE_TEST_UPLOAD_TWO_FILES_TWO_PROJECTS,
                     FileFieldMixin.FILE_TEST_UPLOAD_TWO_FILES_SAME_PROJECT
                     }


def map_data_provider():
    map_dir = pathlib.Path(__file__).parent.joinpath("sample_maps").resolve()

    names = []
    for filename in os.listdir(map_dir):
        fullname = os.path.join(map_dir, filename)
        if os.path.isfile(fullname) and fullname.endswith(".npz"):
            for n in USEFUL_TEST_CASES:
                names.append((fullname, None, n))

    return names
