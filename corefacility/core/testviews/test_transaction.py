from rest_framework.views import APIView
from rest_framework.response import Response

from core.entity.group import Group
from core.permissions import AdminOnlyPermission
from core.transaction import CorefacilityTransaction


class TestTransaction(APIView):
    """
    This is the test view that shall be used transactions.
    """

    permission_classes = [AdminOnlyPermission]

    def get(self, request, *args, **kwargs):
        return self.do_sample_request(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.do_sample_request(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.do_sample_request_no_transaction(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.do_closed_transaction(request, *args, **kwargs)

    def do_sample_request(self, request, *args, dirname=None, **kwargs):
        """
        Lists the directory and saves the listing result to the log file

        :param request: the request to be executed
        :param args: arguments from the request path
        :param dirname: the directory name extracted from the request pathj
        :param kwargs: keyword arguments from the request path
        :return: the response to be sent to the client application
        """
        with CorefacilityTransaction() as transaction:
            group = Group(name="The Some Group", governor=request.user)
            group.create()
            transaction.command_maker.add_command(("ls", "-l", dirname))
        return Response()

    def do_sample_request_no_transaction(self, request, *args, dirname=None, **kwargs):
        """
        Tries to execute command from the command maker without being wrapped to the corefacility transaction

        :param request: the request received from the client application
        :param args: the arguments from the request path
        :param dirname: the directory name from the request path
        :param kwargs: the keyword arguments from the request path
        :return: the response to be sent to the client application
        """
        group = Group(name="The Some Group", governor=request.user)
        group.create()
        from core.os import CommandMaker
        CommandMaker().add_command(("ls", "-l", dirname))
        return Response()

    def do_closed_transaction(self, request, *args, dirname=None, **kwargs):
        """
        Tries to execute the closed transaction

        :param request: the request received from the client application
        :param args: arguments extracted from the request path
        :param kwargs: keyword arguments extracted from the request path
        :param dirname: the directory name extracted from the request path
        :return: the response that will be sent to the client application
        """
        with CorefacilityTransaction() as transaction1:
            group1 = Group(name="The Some Group", governor=request.user)
            group1.create()
            transaction1.command_maker.add_command(("ls", "-l", dirname))
            with CorefacilityTransaction() as transaction2:
                group2 = Group(name="The Other Group", governor=request.user)
                group2.create()
                transaction2.command_maker.add_command(("ls", "-l", "/var/log"))
        return Response()
