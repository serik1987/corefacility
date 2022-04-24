import logging
from time import sleep

from django.shortcuts import render

from core.entity.log import Log

logger = logging.getLogger("django.corefacility.test")


def test_concurrent(request):
    try:
        log = Log.current()
        sleep(10.0)
        print(id(log), log.id)
    except Exception as e:
        logger.warning("The test is not possible during the GET request and when debug is OFF",
                       extra={"request": request})
    return render(request, "core/tests/test.html")
