from plugins.base_plugin import BasePlugin


class MotoGPPlugin(BasePlugin):

    @property
    def name(self):
        return "MotoGP"

    @property
    def filename(self):
        return "motogp.ics"

    def get_events(self):
        return []