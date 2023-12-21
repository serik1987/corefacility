import re
import subprocess
from datetime import datetime

import psutil
from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..management.commands.health_check import Command as HealthChecker


class SystemInformationView(APIView):
    """
    Provides general information about the system.
    """

    CPU_INFORMATION_FILE = "/proc/cpuinfo"
    SUPPORTED_PLATFORMS = {
        "Linux": psutil.LINUX,
        "Microsoft Windows": psutil.WINDOWS,
        "Max OS X": psutil.MACOS,
        "Free BSD": psutil.FREEBSD,
        "Net BSD": psutil.NETBSD,
        "Open BSD": psutil.OPENBSD,
        "BSD": psutil.BSD,
        "Sun OS": psutil.SUNOS,
        "AIX": psutil.AIX,
    }

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Provides general information about the system.

        :param request: the request received from the Web client
        :param args: arguments revealed from parsing the request URI
        :param kwargs: keyword arguments revealed from parsing the request URI
        """
        system_information = dict()
        self._fill_uptime(system_information)
        self._fill_cpu_usage(system_information)
        self._fill_memory_usage(system_information)
        self._fill_disk_usage(system_information)
        self._fill_network_usage(system_information)
        self._fill_software_settings(system_information)

        if settings.CORE_IS_POSIX:
            self._fill_cpu_info(system_information)

        return Response(system_information)

    def _fill_uptime(self, system_information):
        """
        Fills the system information by the uptime data

        :param system_information: a dictionary that will be filled by the uptime data.
        """
        current_time = datetime.now()
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = (current_time - boot_time).total_seconds()
        system_information.update({
            'datetime': current_time,
            'uptime': uptime,
        })

    def _fill_cpu_usage(self, system_information):
        """
        Fills the system information by the CPU usage

        :param system_information: a dictionary that will be filled by the uptime data.
        """
        system_information['cpu_info'] = {
            'load_average': psutil.getloadavg(),
            'cores': psutil.cpu_count(logical=True),
        }

    def _fill_cpu_info(self, system_information):
        """
        Fills the system information by the CPU info.
        This is assumed that the system information has been filled by the CPU usage and the operating system is POSIX
        compatible.

        :param system_information: the system information dictionary to be filled
        """
        cpu_information = list()
        with open(self.CPU_INFORMATION_FILE, 'r') as cpu_information_file:
            core_information = dict()
            for cpu_information_string in cpu_information_file:
                try:
                    key, value = cpu_information_string.split(':', 1)
                except ValueError:
                    cpu_information.append(core_information)
                    core_information = dict()
                key, value = key.strip(), value.strip()
                core_information[key] = value
            if len(core_information) > 0:
                cpu_information.append(core_information)

        if len(cpu_information) > 0:
            system_information['cpu_info']['name'] = cpu_information[0]['model name']

    def _fill_memory_usage(self, system_information):
        """
        Fills the system information dictionary by the memory usage information

        :param system_information: the system information dictionary
        """
        memory_usage = psutil.virtual_memory()
        swap_usage = psutil.swap_memory()
        system_information['memory_info'] = {
            'available': memory_usage.available,
            'total': memory_usage.total,
        }
        system_information['swap_info'] = {
            'available': swap_usage.free,
            'total': swap_usage.total,
        }

    def _fill_disk_usage(self, system_information):
        """
        Fills the system information by the disk usage information

        :param system_information: the system information dictionary
        """
        if not settings.CORE_IS_POSIX:
            return

        mount_points = dict()
        for mount_point in HealthChecker.read_mount_points():
            disk_usage = psutil.disk_usage(mount_point)
            mount_points[mount_point] = {
                'available': disk_usage.free,
                'total': disk_usage.total,
            }

        system_information['disk_info'] = mount_points

    def _fill_network_usage(self, system_information):
        """
        Fills the system information by the network usage

        :param system_information: the system information dictionary
        """
        network_usage = psutil.net_io_counters(pernic=False, nowrap=True)
        system_information['network_info'] = {
            'hostname': subprocess.run(('hostname',), stdout=subprocess.PIPE).stdout.strip(),
            'bytes_sent': network_usage.bytes_sent,
            'bytes_received': network_usage.bytes_recv,
            'packets_sent': network_usage.packets_sent,
            'packets_received': network_usage.packets_recv,
            'errors_input': network_usage.errin,
            'errors_output': network_usage.errout,
            'drops_input': network_usage.dropin,
            'drops_output': network_usage.dropout,
        }

    def _fill_software_settings(self, system_information):
        """
        Fills the information about the operating system

        :param system_information: the system information to be filled
        """
        platform = None
        for platform_name, is_supported in self.SUPPORTED_PLATFORMS.items():
            if is_supported:
                platform = platform_name
        if platform is None:
            platform = _("Unrecognized platform")
        system_information['os_info'] = {'platform': platform}

        system_information['os_info']['posix'] = psutil.POSIX
        if psutil.POSIX:
            system_information['os_info'].update({
                'kernel_version': subprocess.run(('uname', '-r'), stdout=subprocess.PIPE).stdout.strip(),
                'architecture': subprocess.run(('uname', '-p'), stdout=subprocess.PIPE).stdout.strip(),
                'os_version': subprocess.run(('uname', '-v'), stdout=subprocess.PIPE).stdout.strip(),
            })
