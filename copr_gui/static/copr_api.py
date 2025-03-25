from copr import v3
from cached_store import CallCacheMock, CallCache


class CachedClient:
    def __init__(self, client):
        self.__client = client
        self.__cache = CallCache()

    def __call__(self):
        return CallCacheMock(self.__client, self.__cache)


def create_from_config_file(path):
    client = v3.Client.create_from_config_file(path)
    client.cached = CachedClient(client)
    return client
