import re

from .base_window import BaseWindow


class SettingsWindow(BaseWindow):
    """
    Defines the settings window
    """

    template_name = "core/settings.html"
    css_template = re.compile(r'^settings\..+\.css$')
    js_template = re.compile(r'^settings\..+\.js$')
