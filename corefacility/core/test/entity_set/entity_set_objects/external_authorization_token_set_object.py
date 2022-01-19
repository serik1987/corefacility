from random import randrange

from .entity_set_object import EntitySetObject


class ExternalAuthorizationTokenSetObject(EntitySetObject):
    """
    Creates a list of external authorization tokens and manages such a list
    """

    TOKEN_NUMBER = 5
    MAX_AUTH_CODE = 1000000

    _entity_class = None

    def data_provider(self):
        auth_codes = ["%d === TEST AUTHORIZATION CODE ===" % randrange(self.MAX_AUTH_CODE)
                      for n in range(self.TOKEN_NUMBER)]
        kwarg_list = [dict(code=auth_code) for auth_code in auth_codes]
        return kwarg_list
