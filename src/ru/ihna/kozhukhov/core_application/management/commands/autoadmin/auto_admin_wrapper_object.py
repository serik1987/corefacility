from ....exceptions.entity_exceptions import NoLogException
from ....models import PosixRequest
from .auto_admin_object import AutoAdminObject
from .utils import serialize_all_args


class AutoAdminWrapperObject(AutoAdminObject):
    """
    This is a wrapper that shall be used by all methods processing the HTTP request in order to save all commands
    requiring 'root' privileges to the database.

    If Django views and corefacility entity providers try to run something that requires administrative privileges,
    they can't run it directly because worker process doesn't run under 'root'. However, they can use this wrapper
    class in order to save their requirements to the database. Next, a special corefacility process called 'autoadmin'
    that has run under 'root' privileges will load such an action from the database and execute it.
    """

    _wrapped = None
    """ Wrapped object """

    _constructor_args = None
    """ Arguments that were used for the construction routines """

    _constructor_kwargs = None
    """ Keyword arguments that has used for the constructor """

    def __init__(self, wrapped_class, *args, **kwargs):
        """
        Constructs the wrapper together with the wrapped object

        :param wrapped_class: class the wrapped object belongs to
        :param args: positioned arguments to be passed to the constructor of the wrapped class
        :param kwargs: keyword arguments to be passed to the constructor of the wrapped class
        """
        super().__init__()
        self._wrapped = wrapped_class(*args, **kwargs)
        self._constructor_args = args
        self._constructor_kwargs = kwargs
        self.log = self._wrapped.log

    def __getattr__(self, name):
        """
        Accesses the attribute of the wrapped object given that the same attribute doesn't exist in the
        AutoAdminWrapperObject

        :return: If the attribute is not callable, returns the attribute itself. Otherwise, returns the wrapper
        function that stores the callable to the database
        """
        if not hasattr(self._wrapped, name):
            raise AttributeError(
                "Neither 'AutoAdminWrapperObject' nor its wrapped '{wrapped_class}' object contain "
                "the attribute '{attribute}'".format(
                    wrapped_class=self._wrapped.__class__.__name__,
                    attribute=name
                ))

        value = getattr(self._wrapped, name)
        if not callable(value):
            return value

        def auto_admin_wrapper_method(*args, **kwargs):
            if self._wrapped.log is None:
                raise NoLogException(self._wrapped)
            posix_request = PosixRequest(
                action_class="{0}.{1}".format(self._wrapped.__module__, self._wrapped.__class__.__name__),
                action_arguments=serialize_all_args(*self._constructor_args, **self._constructor_kwargs),
                method_name=value.__name__,
                method_arguments=serialize_all_args(*args, **kwargs),
                log_id=self._wrapped.log.id,
            )
            posix_request.save()

        return auto_admin_wrapper_method
