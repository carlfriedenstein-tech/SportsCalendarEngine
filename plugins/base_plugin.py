from abc import ABC, abstractmethod


class BasePlugin(ABC):

    version = "1.0"
    enabled = True

    @property
    @abstractmethod
    def name(self):
        """Display name of the plugin."""
        pass

    @property
    @abstractmethod
    def filename(self):
        """Output ICS filename."""
        pass

    @abstractmethod
    def get_events(self):
        """Return a list of CalendarEvent objects."""
        pass

    def before_run(self):
        """Optional hook executed before get_events()."""
        pass

    def after_run(self, events):
        """Optional hook executed after get_events()."""
        return events