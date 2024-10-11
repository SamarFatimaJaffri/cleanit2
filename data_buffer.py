from metaclass import Singleton


class Data(metaclass=Singleton):
    def __init__(self):
        self._data = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @staticmethod
    def columns():
        if Data.data is None:
            return
        return Data.data.columns.tolist()
