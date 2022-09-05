from uuid import UUID
import json

from django.views.generic import TemplateView

from core import App
from core.entity.corefacility_module import CorefacilityModuleSet
from core.entity.entry_points import AuthorizationsEntryPoint
from core.generic_views import SetCookieMixin


class MainWindow(SetCookieMixin, TemplateView):
    """
    Loading the application main window
    """

    client_version = "v1"
    template_name = "core/index.html"
    css_name = "main.min.css"
    js_name = "main.min.js"

    kwargs = None
    module_set = None

    def __init__(self, *args, **kwargs):
        """
        Initializes the view

        :param args: standard view arguments
        :param kwargs: standard view keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.module_set = CorefacilityModuleSet()
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
        self._split_application_path(path)
        app = self._get_uuid(uuid)
        css_name = "%s/%s" % (app, self.css_name)
        js_name = "%s/%s" % (app, self.js_name)
        self._authorize_user()
        self._set_api_version()
        dump = json.dumps(kwargs)
        return super().get_context_data(js_settings=dump, css=css_name, js=js_name)

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.
        Also, sets the cookie to the response

        Pass response_kwargs to the constructor of the response class.
        """
        response = super().render_to_response(context, **response_kwargs)
        self.set_cookie(self.request, response, refresh=True)
        return response

    def _split_application_path(self, path):
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
        self.kwargs['frontend_route'] = ("/%s/" % self.kwargs['frontend_route']).replace("//", "/")
        self.kwargs['iframe_route'] = ("%s/" % self.kwargs['iframe_route']).replace("//", "/")
        if self.kwargs['iframe_route'][0] == "/":
            self.kwargs['iframe_route'] = self.kwargs['iframe_route'][1:]

    def _get_uuid(self, uuid):
        if uuid is None:
            app = App()
            uuid = str(App().uuid)
        else:
            app = self.module_set.get(uuid)
            uuid = str(uuid)
        self.kwargs['app_uuid'] = uuid
        return app.__module__

    def _authorize_user(self):
        entry_point = AuthorizationsEntryPoint()
        auth_user = None
        for auth_module in entry_point.modules():
            auth_user = auth_module.try_ui_authorization(self.request)
            if auth_user is not None and auth_user.is_locked:
                auth_user = None
            if auth_user is not None:
                self.request.user = auth_user
                break
        if auth_user is not None:
            token = auth_module.issue_token(auth_user)
            self.kwargs['authorization_token'] = token
        else:
            self.kwargs['authorization_token'] = None

    def _set_api_version(self):
        self.kwargs['client_version'] = str(self.client_version)
