from django.conf import settings

from ..utils import get_ip
from ..entity.log import Log

import logging


class LogMiddleware:
    """
    Provides an appropriate logging for responses
    """

    NON_LOGGING_METHOD = ['GET', 'HEAD', 'CONNECT', 'TRACE', 'OPTIONS']

    _get_response = None

    def __init__(self, get_response):
        """
        Initializes the middleware

        :param get_response: the response processing function
        """
        self._get_response = get_response

    def __call__(self, request):
        """
        Initializes creation of the request logs by filling the request details
        :param request: the request to be filled
        :return: nothing
        """
        self.process_request(request)
        response = self._get_response(request)
        if hasattr(request, "corefacility_log"):
            self.process_response(request.corefacility_log, response)
        return response

    def process_request(self, request):
        """
        Initializes the request log and fills request details to it

        :param request: the request which log shall be created
        :return: nothing
        """
        if settings.DEBUG or request.method not in self.NON_LOGGING_METHOD or \
                (request.method == 'GET' and 'activation_code' in request.GET):
            try:
                ip_address = get_ip(request)
                log = Log(log_address=request.path, request_method=request.method, ip_address=ip_address)
                """
                if len(request.FILES) == 0:
                    try:
                        log.request_body = request.body.decode(encoding='utf-8')[:Log.TEXT_MAX_LENGTH]
                    except RawPostDataException:
                        log.request_body = request.data.decode(encoding='utf-8')[:Log.TEXT_MAX_LENGTH]
                """
                log.request_date.mark()
                try:
                    log.request_body = request.body.decode("utf-8")
                except Exception as e:
                    log.request_body = "<i>Not available</i>"
                log.create()
                request.corefacility_log = log
                request.corefacility_log_middleware = self
            except Exception as e:
                logging.getLogger('django.corefacility.log').error(
                    "Unable to insert the log to the database due to the following error: " + str(e)
                )

    def process_view(self, request, callback, callback_args, callback_kwargs):
        """
        Continues the request log processing by attaching the log processing information to the request

        :param request: the request to be processed
        :param callback: some callback
        :param callback_args: callback arguments
        :param callback_kwargs: callback keywords
        :return: nothing
        """
        try:
            callback_doc = callback.__doc__
            if hasattr(request, "corefacility_log") and callback_doc is not None:
                operation_description = callback.__doc__.strip().split("\n")[0].strip()
                request.corefacility_log.operation_description = operation_description
                request.corefacility_log.update()
        except Exception as e:
            logging.getLogger('django.corefacility.log').error(
                "Unable to insert the log to the database due to the following error: " + str(e)
            )

    def process_exception(self, request, exception):
        """
        Continues the request log processing in case of error by filling the error information to the request

        :param request: The request to be processed
        :param exception: the raising exception
        :return: nothing
        """
        pass

    def process_response(self, log, response):
        """
        Writes the final response information to the request log and finishes the request log creation.

        :param log: The log object where request processing details will be saved
        :param response: the response to be processed
        :return: nothing
        """
        try:
            log.response_status = response.status_code
            if not response.streaming and log.response_body != "***":
                log.response_body = response.content.decode(encoding="utf-8")[:Log.TEXT_MAX_LENGTH]
            log.update()
        except Exception as e:
            logging.getLogger('django.corefacility.log').error(
                "Unable to insert the log to the database due to the following error: " + str(e)
            )
