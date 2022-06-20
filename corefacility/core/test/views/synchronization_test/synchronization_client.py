from time import sleep

from rest_framework import status

class SynchronizationClient:
    """
    Provides the sychronization routines for testing purposes given that
    accounts are completely different
    """

    MAX_REQUESTS = 200
    SLEEP_TIME = 1.0

    client = None
    test_module = None
    headers = None
    method = None

    _details = None

    def __init__(self, client, test_module, headers):
        """
        Initializes the synchronization client

        :param client: the API client that shall be used for interations with the server
        :param test_module: a module that is used for the testing purpose
        :param headers: the authorization headers
        """
        self.client = client
        self.test_module = test_module
        self.headers = headers

    @property
    def details(self):
        """
        Details of the last synchronization
        """
        return self._details

    def synchronize(self):
        """
        Performs the synchronization process

        :return: nothing
        """
        print("Synchronization test started.")
        self._details = []
        sync_path = self.test_module.synchronization_path
        sync_data = None
        requests = 0
        sync_started = False
        while not sync_started or sync_data is not None:
            response = self.client.post(sync_path, data=sync_data, format="json", **self.headers)
            sync_started = True
            self.test_module.assertEquals(response.status_code, status.HTTP_200_OK, "Unexpected status code")
            self.test_module.assertIn("next_options", response.data, "The response body shall contain next_url field")
            self.test_module.assertIn("details", response.data, "The response body shall contain details field")
            self._details.extend(response.data['details'])
            sync_data = response.data['next_options']
            print("Next synchronization stage: " + str(sync_data))
            print("Synchronization details: " + str(self.details))
            requests += 1
            if requests > self.MAX_REQUESTS:
                self.test_module.fail("Maximum request number exceeded")
            sleep(self.SLEEP_TIME)
        print("Synchronization test completed.")
