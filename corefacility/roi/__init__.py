from imaging.entity.entry_points.processors import ImagingProcessor


class App(ImagingProcessor):
    """
    Defines the basic interaction between ROI plotter and the functional map facility
    """
    def get_alias(self):
        return "roi"

    def get_name(self):
        return "ROI definition"

    def get_serializer_class(self):
        from core.serializers import ApplicationSettingsSerializer
        return ApplicationSettingsSerializer
