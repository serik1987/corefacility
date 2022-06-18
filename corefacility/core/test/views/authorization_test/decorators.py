from functools import wraps


def enable_single_method(test_function):
    """
    Runs the authorization test when only single authorization method is enabled

    :param test_function: method to run
    :return: decorated function
    """
    @wraps(test_function)
    def completed_test(self, *args, **kwargs):
        for auth_module in self.auth_ep.modules(is_enabled=False):
            auth_module.is_enabled = auth_module.alias == self.method_alias
            auth_module.update()
        test_function(self, *args, **kwargs)
    return completed_test


def enable_all_methods(test_function):
    """
    Runs the authorization test when all authorization methods are enabled
    
    :param test_function: method to run
    :return: decorating function
    """
    @wraps(test_function)
    def completed_test(self, *args, **kwargs):
        for auth_module in self.auth_ep.modules(is_enabled=False):
            auth_module.is_enabled = True
            auth_module.update()
        test_function(self, *args, **kwargs)
    return completed_test


def disable_all_methods(test_function):
    """
    Runs the authorization test when all methods are disabled

    :param test_function: tested function
    :return: decorated function
    """
    @wraps(test_function)
    def completed_test_function(self, *args, **kwargs):
        for auth_module in self.auth_ep.modules():
            auth_module.is_enabled = False
            auth_module.update()
        test_function(self, *args, **kwargs)
    return completed_test_function
