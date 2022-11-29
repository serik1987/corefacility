import os

from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import BadRequest
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.staticfiles import finders

from core.generic_views import SetCookieMixin
from core.entity.corefacility_module import CorefacilityModuleSet


class BaseWindow(SetCookieMixin, TemplateView):
    """
    This is the base class for all types of UIs: settings forms, applications interfaces etc.
    """

    language_code = settings.LANGUAGE_CODE.split('-')[0]

    css_template = None
    js_template = None

    _css_name = None
    _js_name = None

    _app_module = None

    def __init__(self, *args, **kwargs):
        """
        Initializes the view

        :param args: standard view arguments
        :param kwargs: standard view keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.module_set = CorefacilityModuleSet()

    @property
    def js_name(self):
        """
        The full path to the window frontend (the Javascript code)
        """
        if self.js_template is None:
            raise NotImplementedError("The js_template property is undefined")
        if self._js_name is None:
            self._js_name = self._find_frontend(self.js_template)
        return self._js_name

    @property
    def css_name(self):
        """
        The full path to the frontend CSS styles (the CSS code)
        """
        if self.css_template is None:
            raise NotImplementedError("The css_template property is undefined")
        if self._css_name is None:
            self._css_name = self._find_frontend(self.css_template)
        return self._css_name

    def get_context_data(self, uuid=None, **kwargs):
        """
        Transforms the path argument to the context arguments

        :param uuid: The application UUID
        :param kwargs: the dictionary that includes the path argument
        :return: nothing
        """
        if self._app_module is None and uuid is not None:
            app = self.module_set.get(uuid)
            self._app_module = app.__module__
        return super().get_context_data(
            language_code=self.language_code,
            css=self.css_name,
            js=self.js_name,
            **kwargs
        )

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

    def _find_frontend(self, frontend_template):
        frontend_location = finders.find(self._app_module)
        filename = None
        for current_filename in os.listdir(frontend_location):
            if frontend_template.match(current_filename):
                filename = "%s/%s" % (self._app_module, current_filename)
        if filename is None:
            raise BadRequest("The requested module exists but doesn't have frontend available to access this feature")
        return filename
