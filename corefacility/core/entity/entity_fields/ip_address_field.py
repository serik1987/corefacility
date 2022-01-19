from ipaddress import ip_address

from .entity_field import EntityField


class IpAddressField(EntityField):
    """
    Defines a field for storing and retrieving the IP adress.
    """

    def __init__(self, description: str = None):
        """
        Intializes the IP address field

        :param description: field description
        """
        super().__init__(str, description=description)

    def proofread(self, value):
        """
        Transforms the field from the internal string to the public string

        :param value: internal representation of the IP address
        :return: public representation of the IP address
        """
        if value is not None:
            value = ip_address(value)
        return value

    def correct(self, value):
        """
        Transforms the value from public representation to the internal representation

        :param value: public representation value
        :return: internal representation of the IP address
        """
        if value is not None:
            value = str(ip_address(value))
        return value
