from metaclass import Singleton


class Session(metaclass=Singleton):
    def __init__(self):
        self._provider = ''
        self._API_KEY = ''

    @property
    def provider(self):
        return self._provider

    @provider.setter
    def provider(self, provider):
        self._provider = provider

    @property
    def api_key(self):
        return self._API_KEY

    @api_key.setter
    def api_key(self, API_KEY):
        self._API_KEY = API_KEY
