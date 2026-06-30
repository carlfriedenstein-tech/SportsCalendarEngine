from abc import ABC, abstractmethod


class BasePlugin(ABC):

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def filename(self):
        pass

    @abstractmethod
    def get_events(self):
        pass