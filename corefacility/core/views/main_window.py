import re
import json

from django.conf import settings

from core import App
# The core application has one unique feature: you don't have to give its UUID.
# Any other applications require UUID!

from core.authorizations.password_recovery import PasswordRecoveryAuthorization
# Password recovery authorization is needed to detect whether the activation mail
# can be sent to the user or not

from core.entity.entry_points import AuthorizationsEntryPoint
from core.entity.entity_exceptions import AuthorizationException

from .base_window import BaseWindow


class MainWindow(BaseWindow):
    """
    Loading the application main window
    """
    client_version = "v1"
    template_name = "core/index.html"
    css_template = re.compile(r'^main\..+\.css$')
    js_template = re.compile(r'^main\..+\.js$')

    kwargs = None
    module_set = None

    def __init__(self, *args, **kwargs):
        """
        Initializes the view

        :param args: standard view arguments
        :param kwargs: standard view keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.module_set.is_enabled = True
        self.module_set.is_application = True

    def get_context_data(self, path='', uuid=None, **kwargs):
        """
        Transforms the path argument to the context arguments
        :param path: The accessing resource path
        :param uuid: The application UUID
        :param kwargs: the dictionary that includes the path argument
        :return: nothing
        """
        self.kwargs = kwargs
        self.split_application_path(path)
        self._evaluate_uuid(uuid)
        self._authorize_user()
        self._set_static_options()
        kwargs['module_path'] = self._app_module
        dump = json.dumps(kwargs)
        return super().get_context_data(js_settings=dump, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.

        Pass response_kwargs to the constructor of the response class.
        """
        response = super().render_to_response(context, **response_kwargs)
        entry_point = AuthorizationsEntryPoint()
        for module in entry_point.modules():
            response.delete_cookie(module.get_alias())
        return response

    def split_application_path(self, path):
        routes = path.split("/apps/", 1)
        if len(routes) == 2:
            another_routes = routes[1].split("/", 1)
            if len(another_routes) == 2:
                self.kwargs['frontend_route'] = routes[0] + "/apps/" + another_routes[0]
                self.kwargs['iframe_route'] = another_routes[1]
            else:
                self.kwargs['frontend_route'] = routes[0] + "/apps/" + another_routes[0]
                self.kwargs['iframe_route'] = ""
        else:
            self.kwargs['frontend_route'] = path
            self.kwargs['iframe_route'] = ""
        self.kwargs['frontend_route'] = ("/%s/" % self.kwargs['frontend_route']).replace("//", "/").replace("//", "/")
        self.kwargs['iframe_route'] = ("%s/" % self.kwargs['iframe_route']).replace("//", "/")
        if self.kwargs['iframe_route'][0] == "/":
            self.kwargs['iframe_route'] = self.kwargs['iframe_route'][1:]

    def _evaluate_uuid(self, uuid):
        """
        Evaluates the application UUID
        :param uuid: the UUID to evaluate
        :return: nothing
        """
        if uuid is None:
            app = App()
        else:
            app = self.module_set.get(uuid)
        serializer = app.get_serializer_class()(app)
        self.kwargs['app'] = serializer.data
        self._app_module = app.__module__

    def _authorize_user(self):
        try:
            entry_point = AuthorizationsEntryPoint()
            auth_user = None
            module_alias = None
            for auth_module in entry_point.modules():
                auth_user = auth_module.try_ui_authorization(self.request, self)
                if auth_user is not None and auth_user.is_locked:
                    auth_user = None
                if auth_user is not None:
                    self.request.user = auth_user
                    module_alias = auth_module.get_alias()
                    break
            if auth_user is not None:
                if not hasattr(self, 'authentication_token'):
                    token = auth_module.issue_token(auth_user)
                    self.kwargs['authorization_token'] = token
                else:
                    self.kwargs['authorization_token'] = self.authentication_token
            else:
                self.kwargs['authorization_token'] = None
            self.kwargs['authorization_error'] = None
        except AuthorizationException as exception:
            self.split_application_path(exception.route)
            self.kwargs['authorization_token'] = None
            self.kwargs['authorization_error'] = str(exception)


    def _set_static_options(self):
        self.kwargs['client_version'] = str(self.client_version)
        self.kwargs['lang'] = str(self.language_code)
        self.kwargs['email_support'] = settings.EMAIL_SUPPORT
        self.kwargs['suggest_administration'] = settings.CORE_SUGGEST_ADMINISTRATION
        if hasattr(self.request, 'password'):
            self.kwargs['login'] = self.request.user.login
            self.kwargs['password'] = self.request.password
