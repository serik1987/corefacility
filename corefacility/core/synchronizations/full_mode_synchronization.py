from core.entity.entry_points.synchronizations import SynchronizationModule
from core.entity.user import User, UserSet
from core.entity.entity_exceptions import EntityNotFoundException

from .exceptions import UserRemoveConsistencyError


class FullModeSynchronization(SynchronizationModule):
    """
    The is the base class for all synchronizers that work in so called 'full mode'.

    The 'full mode' means that the synchronizer is able to download the full user list
    from the remote server, add all missing users, update the user information up to the
    relevant one and delete all users that don't exist in the remote server.
    """

    DEFAULT_MAX_REMOVED_USERS = 20
    """ Default number of maximum removed users """

    DEFAULT_AUTO_ADD = True
    """ The default value of the auto_add property """

    DEFAULT_AUTO_UPDATE = True
    """ The default value of the auto_update property """

    DEFAULT_AUTO_REMOVE = True
    """ The default value of the auto_remove property """

    def get_auto_add(self):
        """
        Returns True if new accounts shall be created when they exist in the remote
        server but are missing in the current server.

        :return: True of False
        """
        return self.user_settings.get("auto_add", self.DEFAULT_AUTO_ADD)

    def get_auto_update(self):
        """
        Returns True if new accounts shall be updated when they exist in the current server
        and they exist in the remote server

        :return: True or False
        """
        return self.user_settings.get("auto_update", self.DEFAULT_AUTO_UPDATE)

    def get_auto_remove(self):
        """
        Returns True if new accounts shall be removed when they exist in the current server
        but are missing in the remote server.

        :return: True or False
        """
        return self.user_settings.get("auto_remove", self.DEFAULT_AUTO_REMOVE)

    def synchronize(self, action="download", **options):
        """
        Provides an account synchronization

        :param action: one of the following actions:
            'download' downloads a certain portion of data from the external source. All missing accounts will
            be added, all existing accounts will be updated
            'inverse' change list of updated users to the list of missing users
            'remove' remove all inexistent users from the list
        :param options: the synchronization options. The synchronization must be successfuly started and successfully
            completed when no options are given.
        :return: a dictionary that contains the following fields:
            next_options - None if synchronization shall be completed. If synchronization has not been completed
                this function shall be run repeatedly with the option mentioned in this field.
                Please, note that not all options can be passed back using the URL get parameters
            details - some information about all completed actions. The information is useful to be printed out.
        """
        if action == "download":
            result = self.download(**options)
        elif action == "inverse":
            result = self.inverse(**options)
        elif action == "remove":
            result = self.remove(**options)
        else:
            result = self.download(**options)
        return result

    def download(self, updated_users=None, **options):
        """
        Downloads the user list from the external server, adds all missing users and updates
        all users that have already been present

        :param updated_users: List of IDs of all users that has already been added or updated by the previous
            method call
        :param options: another class-specific options
        :return: the output to be returned to the client
        """
        if not isinstance(updated_users, list):
            updated_users = []
        user_set = UserSet()
        user_set.is_support = False
        raw_data = self.get_raw_data(**options)
        details = []
        for user_login, user_kwargs in self.find_user(raw_data, **options):
            try:
                user = user_set.get(user_login)
                if self.get_auto_update():
                    update_required = False
                    for name, value in user_kwargs.items():
                        setattr(user, name, value)
                        update_required = True
                    if update_required:
                        user.update()
                    updated_users.append(user.id)
            except EntityNotFoundException:
                try:
                    if self.get_auto_add():
                        user = User(**user_kwargs)
                        user.create()
                        updated_users.append(user.id)
                except Exception as exc:
                    details.append(self.error_message(user_kwargs, "add", exc))
            except Exception as exc:
                details.append(self.error_message(user_kwargs, "update", exc))
        print(options)
        next_options = self.get_next_options(raw_data, **options)
        if next_options is None:
            next_options = {"action": "inverse"}
        else:
            next_options['action'] = "download"
        next_options["updated_users"] = updated_users
        return {
            "next_options": next_options,
            "details": details,
        }

    def inverse(self, **options):
        """
        Accepts the 'updated_users' option that contains list of all users that have been found in the list
        and have been added or modified.

        Returns number of all users that are missed on the external website. Such users are candidates for
        the removal.

        :param options: information about all added or modified users
        :return: information about all removed users
        """
        next_options = None
        details = []
        try:
            updated_users = set(options['updated_users'])
            all_users = set()
            user_set = UserSet()
            user_set.is_support = False
            for user in user_set:
                all_users.add(user.id)
            removing_users = all_users - updated_users
            next_options = {
                "action": "remove",
                "removing_users": list(removing_users)
            }
        except Exception as exc:
            details = [self.error_message({}, "inverse", exc)]
        return {"next_options": next_options, "details": details}

    def remove(self, **options):
        next_options = None
        details = None
        try:
            removing_users = set(options['removing_users'])
            print(removing_users)
            user_set = UserSet()
            user_set.is_support = False
            details = []
            counter = 0
            while len(removing_users) > 0:
                user_id = removing_users.pop()
                user_kwargs = {}
                try:
                    user = user_set.get(user_id)
                    user_kwargs = {
                        "login": user.login,
                        "name": user.name,
                        "surname": user.surname
                    }
                    if isinstance(self.user, User) and self.user.id == user.id:
                        raise UserRemoveConsistencyError()
                    user.delete()
                except EntityNotFoundException:
                    pass
                except Exception as exc:
                    details.append(self.error_message(user_kwargs, "remove", exc))
                counter += 1
                if counter >= self.DEFAULT_MAX_REMOVED_USERS:
                    break
            if len(removing_users) > 0:
                next_options = {"action": "remove", "removing_users": list(removing_users)}
        except Exception as exc:
            details = [self.error_message({}, "remove", exc)]
        return {"next_options": next_options, "details": details}

    def get_raw_data(self, **options):
        """
        Makes an HTTP request to the external server that uploads certain amount of the user list

        :param options: some request options
        :return: the response body represented as Python's primitives
        """
        raise NotImplementedError("Please, implement the get_raw_data function")

    def find_user(self, raw_data, **options):
        """
        Finds all users in the raw data

        :param raw_data: the raw data returned by the get_raw_data function
        :param options: some request options
        :return: the generator that allows to iterate over (login, user_kwargs) tuples. login is used for searching
            over all users while user_kwargs will during the user create if no user has been found
        """
        raise NotImplementedError("Please, implement the find_user method")

    def get_next_options(self, raw_data, **options):
        """
        If the user downloading process has been completed, the function returns None. Otherwise, it returns the
        options that will be substituted to the get_raw_data during the following data downloading stage

        :param raw_data: the raw data itself
        :param options: some additional options
        :return: True or False
        """
        raise NotImplementedError("Please, implement the get_next_options method")
