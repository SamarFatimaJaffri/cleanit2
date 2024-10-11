from dataclasses import dataclass

from metaclass import Singleton


@dataclass()
class Session(metaclass=Singleton):
    provider: str = ''
    api_key: str = ''
