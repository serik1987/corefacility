from rest_framework import status


def security_test_provider():
    return [
        (None, status.HTTP_401_UNAUTHORIZED),
        ("ordinary_user", status.HTTP_200_OK),
        ("superuser", status.HTTP_200_OK),
    ] + [
        ("user%d" % user_index, status.HTTP_200_OK) for user_index in range(1, 11)
    ]
