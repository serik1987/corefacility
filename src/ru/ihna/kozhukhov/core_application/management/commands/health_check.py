import json
import re
import subprocess
import sys
from datetime import datetime, timedelta
from time import sleep
from logging import getLogger, ERROR

import psutil
from django.conf import settings
from django.core.management import BaseCommand
from django.utils.timezone import make_aware
from django.utils.translation import gettext_lazy as _

from ru.ihna.kozhukhov.core_application.models import HealthCheck
from ru.ihna.kozhukhov.core_application.utils import mail, human_readable_memory, MEGABYTE, GIGABYTE


class Command(BaseCommand):
    """
    Monitors the health status and saves the monitoring results to the database
    """

    MONITORING_INTERVAL = 60
    """ The timestamp in seconds """

    HEALTH_REMOVE_PERIOD = 60
    """
    Maximum number of timestamps required to be elapsed before the system starts recycling of deprecated timestamps 
    """

    VIEW_INTERVAL = timedelta(weeks=1)
    """
    Minimum lifetime of timestamps in the database (the dead timestamps will be removed by the timestamp recycling 
    process)
    """

    STATIONARY_MOUNT_POINT_FILE = "/etc/fstab"
    STATIONARY_MOUNT_POINT_LINE = \
        re.compile(r'^(?P<filesystem>[^#\s]+)\s+(?P<mount_point>[^#\s]+)\s+(?P<type>[^#\s]+)\s+(?P<options>[^#\s]+)\s+'
                   r'(?P<dump>[^#\s]+)\s+(?P<pass>[^#\s]+)(?:\s*#.*)?$')

    TEMPERATURE_KEY = re.compile(r'^temp\d_input$')
    """
    Required for interactions between lm-sensors and corefacility
    """

    CRITICAL_VALUES = {
        "cpu_load": None,
        "ram_free": 100 * MEGABYTE,
        "swap_used": 500 * MEGABYTE,
        "hdd_free": GIGABYTE,
        "bytes_sent": None,
        "bytes_received": None,
        "temperature": 70,
    }
    """
    If the health values exceed these threshold, the system administrators will be warned about this
    """

    EMAIL_PERIOD = timedelta(days=1)
    """
    Minimum amount of duration between two consequtive e-mails. Not valid when the daemon has been reloaded.
    """

    __mount_points = None
    __total_swap = None
    __engaged_swap = None

    __last_email_date = None
    __logger = getLogger("django.corefacility.log")

    @classmethod
    def read_mount_points(cls):
        """
        Reads all mount points from the /etc/fstab file

        :return: list of string containing all mount points
        """
        mount_points = list()

        with open(cls.STATIONARY_MOUNT_POINT_FILE, 'r') as mount_point_file:
            for mount_point_string in mount_point_file:
                mount_point_info = cls.STATIONARY_MOUNT_POINT_LINE.match(mount_point_string)
                if mount_point_info is None:
                    continue
                mount_point = mount_point_info['mount_point']
                if mount_point == 'none':
                    mount_point = None
                if mount_point is not None:
                    mount_points.append(mount_point)

        return mount_points

    def handle(self, *args, **kwargs):
        """
        The infinite loop for the health status monitoring.

        :param args: command-line arguments
        :param kwargs: command-line options
        """
        try:
            self.__mount_points = self.read_mount_points()
            iteration_number = 0
            while True:
                health_check = self._detect_health_check()
                health_check.save()
                criticals = self._detect_criticals(health_check)
                is_critical = False
                for key, values in criticals.items():
                    is_critical = is_critical or values['is_critical']
                if is_critical and (
                        self.__last_email_date is None or health_check.date - self.__last_email_date > self.EMAIL_PERIOD
                ):
                    mail(
                        template_prefix="core/healthcheck_alarm",
                        context_data={
                            'admin_name': settings.ADMIN_NAME,
                            'criticals': criticals,
                        },
                        subject=_("ALARM: critical values of important server health parameters detected"),
                        recipient=settings.ADMIN_EMAIL,
                        fail_silently=True,
                    )
                    self.__last_email_date = health_check.date
                del health_check
                del criticals
                if iteration_number % self.HEALTH_REMOVE_PERIOD == 0:
                    self._recycle_old_timestamps()
                sleep(self.MONITORING_INTERVAL)
                iteration_number += 1
        except KeyboardInterrupt:
            print("The termination signal received.")
        except Exception as error:
            self.__logger.log(ERROR, "corefacility health check error: " + str(error), exc_info=sys.exc_info())

    def _detect_health_check(self):
        """
        Detects the main computer measures

        :return: the HealthCheck object with the main sensor measures
        """
        health_check = HealthCheck()
        health_check.date = make_aware(datetime.now())
        health_check.cpu_load = psutil.cpu_percent(percpu=True)
        health_check.ram_free = psutil.virtual_memory().available
        swap_info = psutil.swap_memory()
        self.__total_swap = swap_info.total
        self.__engaged_swap = swap_info.used
        health_check.swap_free = swap_info.free
        health_check.hdd_free = {mount_point: psutil.disk_usage(mount_point).free
                                 for mount_point in self.__mount_points}
        net_io_counters = psutil.net_io_counters(pernic=False, nowrap=True)
        health_check.bytes_sent = net_io_counters.bytes_sent
        health_check.bytes_received = net_io_counters.bytes_recv
        sensors_info = subprocess.run(('sensors', '-j'), stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        health_check.temperature = json.loads(sensors_info.stdout)
        return health_check

    def _detect_criticals(self, health_check):
        """
        Detects critical values of the health monitor

        :param health_check: a HealthCheck object containing the critical values
        :return: a Python dictionary with ordinary and critical values
        """
        criticals = dict()

        for index, cpu_load in enumerate(health_check.cpu_load):
            criticals["%s %s" % (_("CPU"), index + 1)] = {
                'actual_value': "%1.1f %%" % cpu_load,
                'critical_value': "-",
                'is_critical': False,
            }

        criticals[_("Free operating memory")] = {
            'actual_value': human_readable_memory(health_check.ram_free),
            'critical_value': human_readable_memory(self.CRITICAL_VALUES['ram_free']),
            'is_critical': health_check.ram_free < self.CRITICAL_VALUES['ram_free'],
        }

        criticals[_("Free swap memory")] = {
            'actual_value': human_readable_memory(health_check.swap_free),
            'critical_value': human_readable_memory(self.__total_swap - self.CRITICAL_VALUES['swap_used']),
            'is_critical': self.__engaged_swap > self.CRITICAL_VALUES['swap_used'],
        }

        for mount_point, hdd_free in health_check.hdd_free.items():
            criticals["%s %s" % (_("Free space at"), mount_point)] = {
                'actual_value': human_readable_memory(hdd_free),
                'critical_value': human_readable_memory(self.CRITICAL_VALUES['hdd_free']),
                'is_critical': hdd_free < self.CRITICAL_VALUES['hdd_free'],
            }

        criticals.update(self.__read_critical_temperature(health_check.temperature))

        return criticals

    def __read_critical_temperature(self, temperature):
        """
        Reads the critical temperature from the object received from the sensors command

        :param temperature: the parsed output of the sensors command
        :return: a piece of the criticals
        """
        criticals = dict()

        if isinstance(temperature, dict):
            dictionary_processed = False
            for parent_key, parent_value in temperature.items():
                if not isinstance(parent_value, dict):
                    continue
                for child_key, child_value in parent_value.items():
                    if self.TEMPERATURE_KEY.match(child_key) is not None:
                        criticals["%s %s" % (_("Temperature for"), parent_key)] = {
                            'actual_value': "%1.1f \u00b0C" % child_value,
                            'critical_value': "%1.1f \u00b0C" % self.CRITICAL_VALUES['temperature'],
                            'is_critical': child_value > self.CRITICAL_VALUES['temperature'],
                        }
                        dictionary_processed = True

            if not dictionary_processed:
                for key, value in temperature.items():
                    criticals.update(self.__read_critical_temperature(value))

        return criticals

    def _recycle_old_timestamps(self):
        """
        Recycles the timestamps which lifetime exceed some critical value
        """
        timestamp_birth_threshold = make_aware(datetime.now() - self.VIEW_INTERVAL)
        HealthCheck.objects.filter(date__lte=timestamp_birth_threshold).delete()
