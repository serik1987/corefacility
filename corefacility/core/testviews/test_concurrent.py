from django.shortcuts import render
from time import sleep

from core.entity.log import Log


def test_concurrent(request):
    log = Log.current()
    sleep(10.0)
    print(id(log), log.id)
    return render(request, "core/tests/test.html")
