import re
from datetime import datetime
from dateutil.parser import parse, ParserError

import psutil
from django.utils.timezone import make_aware, is_naive
from django.utils.translation import gettext as _
from django.db.models.manager import Manager
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ru.ihna.kozhukhov.core_application.management.commands.health_check import Command as HealthCheckDaemon
from ru.ihna.kozhukhov.core_application.models import HealthCheck as HealthCheckModel


class HealthCheck(APIView):
    """
    Returns some amount of health check timestamps to the client
    """

    permission_classes = [IsAuthenticated]

    CATEGORIES = ['cpu', 'network', 'disk', 'memory', 'temperature']
    """ The health check category are written by the client in the request path """

    VIRTUAL_MEMORY_INDEX = 0
    """
    The 'memory' category returns the two-channel record: one channel is for physical memory and another one is
    for the swap
    """

    SWAP_MEMORY_INDEX = 1
    """
    The 'memory' category returns the two-channel record: one channel is for physical memory and another one is
    for the swap
    """

    BYTES_SENT_INDEX = 0
    """
    The memory category returns two-channel signal. The first channel is for bytes sent and the another one is for
    bytes received
    """

    BYTES_RECEIVED_INDEX = 1
    """
    The memory category returns two-channel signal. The first channel is for bytes sent and the another one is for
    bytes received
    """

    TEMPERATURE_MATCHER = re.compile(r'^temp\d_input$')
    """
    Name of the field in lm-sensors output that contains actual temperature value
    """

    _previous_bytes_sent = None
    """
    Reflects number of bytes sent at the previous timestamp
    """

    _previous_bytes_received = None
    """
    Reflects number of bytes received at the previous timestamp
    """

    _previous_date = None
    """
    Reflects the date related to the previous timestamp
    """

    _temperature_labels = None
    """ the temperature labels that shall not be changed at least since the last boot """

    def get(self, request, *args, category=None, **kwargs):
        """
        Immediate request processing

        :param request: the request received from the client
        :param args: useless
        :param category: defines what kind of signals to reveal
        :return: the response to be sent to the client
        """
        if category not in self.CATEGORIES:
            raise NotFound()

        current_date = make_aware(datetime.now())
        minimum_date = current_date - HealthCheckDaemon.VIEW_INTERVAL

        health_check_manager = HealthCheckModel.objects
        if 'from' in request.query_params:
            try:
                time = parse(request.query_params['from'])
                if is_naive(time):
                    time = make_aware(time)
            except ParserError:
                raise ValidationError({'from': "Bad date/time format."})
            health_check_manager = health_check_manager.filter(date__gte=time)
        if 'to' in request.query_params:
            try:
                time = parse(request.query_params['to'])
                if is_naive(time):
                    time = make_aware(time)
            except ParserError:
                raise ValidationError({'to': "Bad date/time format."})
            health_check_manager = health_check_manager.filter(date__lte=time)
        if isinstance(health_check_manager, Manager):
            health_check_manager = health_check_manager.all()

        timestamps = []
        values = None
        labels = None
        get_channels = getattr(self, "get_%s_channels" % category)
        fill_values = getattr(self, "fill_%s_values" % category)
        get_labels = getattr(self, "get_%s_labels" % category)
        get_constants = getattr(self, "get_%s_constants" % category)
        for health_check in health_check_manager:
            timestamps.append(health_check.date)
            if labels is None:
                labels = get_labels(health_check)
            if values is None:
                values = [list() for k in range(get_channels(health_check))]
            fill_values(values, health_check)

        return Response({
            'minimum_date': minimum_date.isoformat(timespec='minutes'),
            'current_date': current_date.isoformat(timespec='minutes'),
            'repeat_after': HealthCheckDaemon.MONITORING_INTERVAL,
            'timestamps': timestamps,
            'labels': labels,
            'values': values,
            'constants': get_constants(labels),
        })

    def get_cpu_channels(self, health_check):
        return len(health_check.cpu_load)

    def get_memory_channels(self, health_check):
        return 2

    def get_disk_channels(self, health_check):
        return len(health_check.hdd_free)

    def get_network_channels(self, health_check):
        return 2

    def get_temperature_channels(self, health_check):
        return len(self._temperature_labels)

    def fill_cpu_values(self, values, health_check):
        for cpu_index, load_value in enumerate(health_check.cpu_load):
            values[cpu_index].append(load_value)

    def fill_memory_values(self, values, health_check):
        values[self.VIRTUAL_MEMORY_INDEX].append(health_check.ram_free)
        values[self.SWAP_MEMORY_INDEX].append(health_check.swap_free)

    def fill_disk_values(self, values, health_check):
        labels = self.get_disk_labels(health_check)
        for label, value in health_check.hdd_free.items():
            channel_index = labels.index(label)
            values[channel_index].append(health_check.hdd_free[label])

    def fill_network_values(self, values, health_check):
        if self._previous_bytes_sent is None or self._previous_bytes_received is None or self._previous_date is None:
            values[self.BYTES_SENT_INDEX].append(0)
            values[self.BYTES_RECEIVED_INDEX].append(0)
        else:
            time_period = (health_check.date - self._previous_date).total_seconds()
            values[self.BYTES_SENT_INDEX].append(
                (health_check.bytes_sent - self._previous_bytes_sent) / time_period
            )
            values[self.BYTES_RECEIVED_INDEX].append(
                (health_check.bytes_received - self._previous_bytes_received) / time_period
            )

        self._previous_bytes_sent = health_check.bytes_sent
        self._previous_bytes_received = health_check.bytes_received
        self._previous_date = health_check.date

    def fill_temperature_values(self, values, health_check):
        processed_indices = set()

        def filling_function(key, value):
            try:
                index = self._temperature_labels.index(key)
                if index not in processed_indices:
                    values[index].append(value)
                    processed_indices.add(index)
            except ValueError:
                pass

        self._reduce_temperature_info(health_check.temperature, filling_function)
        for unprocessed_index in set(range(self.get_temperature_channels(health_check))) - processed_indices:
            values[unprocessed_index].append(None)

    def get_cpu_labels(self, health_check):
        return ["%s %d" % (_("CPU"), i+1) for i in range(len(health_check.cpu_load))]


    def get_memory_labels(self, health_check):
        return [_("Free operating memory"), _("Free swap memory")]

    def get_disk_labels(self, health_check):
        return list(health_check.hdd_free.keys())
    
    def get_network_labels(self, health_check):
        return [_("Network output traffic"), _("Network input traffic")]

    def get_temperature_labels(self, health_check):
        self._temperature_labels = self._reduce_temperature_info(health_check.temperature, lambda key, value: key)
        return self._temperature_labels

    def get_cpu_constants(self, labels):
        return {}

    def get_memory_constants(self, labels):
        return {
            'ram_total': psutil.virtual_memory().total,
            'swap_total': psutil.swap_memory().total,
        }

    def get_disk_constants(self, labels):
        return {label: psutil.disk_usage(label).total for label in labels}

    def get_network_constants(self, labels):
        self._previous_bytes_sent = None
        self._previous_bytes_received = None
        self._previous_date = None
        return {}

    def get_temperature_constants(self, labels):
        self._temperature_labels = None
        return {}

    def _reduce_temperature_info(self, temperature, callback):
        reduction = []

        if not isinstance(temperature, dict):
            return reduction

        for parent_key, parent_value in temperature.items():
            if not isinstance(parent_value, dict):
                continue
            for child_key, child_value in parent_value.items():
                if self.TEMPERATURE_MATCHER.match(child_key):
                    reduction.append(callback(parent_key, child_value))

        if len(reduction) == 0:
            for key, value in temperature.items():
                reduction = [*reduction, *self._reduce_temperature_info(value, callback)]

        return reduction
