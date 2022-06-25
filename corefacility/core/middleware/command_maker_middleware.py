from django.conf import settings

from ..os.command_maker import CommandMaker


class CommandMakerMiddleware:

    SAFE_METHODS = ["GET", "HEAD", "CONNECT", "TRACE", "OPTIONS"]

    _get_response = None

    command_maker = None

    def __init__(self, get_response):
        """
        Initializes the middleware.
        This constructor will be automatically run before the processing of each request

        :param get_response: the function that is responsible for processing a particular request
        """
        if settings.CORE_UNIX_ADMINISTRATION or settings.CORE_SUGGEST_ADMINISTRATION:
            self.command_maker = CommandMaker()
        self._get_response = get_response

    def __call__(self, request):
        """
        Provides an immediate request processing

        :param request: the request received from the client
        :return: the response that shall be sent to the client
        """
        if self.command_maker is not None:
            self.command_maker.initialize_executor(request)
        response = self._get_response(request)
        if self.command_maker is not None:
            self.command_maker.clear_executor(request)
        return response
