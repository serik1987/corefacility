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

    def synchronize(self):
        """
        Performs the synchronization process

        :return: nothing
        """
        print("Synchronization test started.")
        sync_path = self.test_module.synchronization_path
        requests = 0
        while sync_path is not None:
            response = self.client.get(sync_path, **self.headers)
            self.test_module.assertEquals(response.status_code, status.HTTP_200_OK, "Unexpected status code")
            self.test_module.assertIn("next_url", response.data, "The response body shall contain next_url field")
            self.test_module.assertIn("details", response.data, "The response body shall contain details field")
            self.process_synchronization_details(response.data['details'])
            sync_path = response.data['next_url']
            print("Next synchronization stage: " + str(sync_path))
            requests += 1
            if requests > self.MAX_REQUESTS:
                self.test_module.fail("Maximum request number exceeded")
            sleep(self.SLEEP_TIME)
        print("Synchronization test completed.")

    def process_synchronization_details(self, details):
        print("Synchronization details received: " + str(details))
