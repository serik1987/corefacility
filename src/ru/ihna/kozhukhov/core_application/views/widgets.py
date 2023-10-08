from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from ..exceptions.entity_exceptions import EntityNotFoundException
from ..entity.corefacility_module import CorefacilityModuleSet
from ..entity.entity_sets.entry_point_set import EntryPointSet


class WidgetsView(APIView):
    """
    Loading the list of available widgets
    """

    permission_classes = []

    def get(self, *args, module_uuid=None, entry_point_alias=None, **kwargs):
        """
        Sends list of available widgets to the client
        :param args: useless
        :param module_uuid: UUID of the module certain entry point belongs to
        :param entry_point_alias: alias of the common entry points all widgets are attached to
        :param kwargs: useless
        :return: the HTTP response
        """
        """
        for module in CorefacilityModuleSet():
            print(module.alias, module.uuid)
        """
        try:
            module = CorefacilityModuleSet().get(module_uuid)
            ep_set = EntryPointSet()
            ep_set.parent_module = module
            entry_point = ep_set.get(entry_point_alias)
        except EntityNotFoundException:
            raise NotFound()
        all_widgets = []
        for uuid, alias, name, html_code in entry_point.widgets(True):
            all_widgets.append({"uuid": str(uuid), "alias": alias, "name": name, "html_code": html_code})
        return Response(all_widgets)
