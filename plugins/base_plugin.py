from abc import ABC, abstractmethod


class BasePlugin(ABC):

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def get_events(self):
        pass