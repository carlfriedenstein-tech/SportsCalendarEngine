from engine.downloader import Downloader
from plugins.base_plugin import BasePlugin


class MotoGPPlugin(BasePlugin):

    EVENTS_URL = "https://api.pulselive.motogp.com/motogp/v1/events?seasonYear=2026"

    @property
    def name(self):
        return "MotoGP"

    @property
    def filename(self):
        return "motogp.ics"

    def download(self):
        return Downloader().get_json(self.EVENTS_URL)

    def parse(self, events):

        print(f"Downloaded {len(events)} MotoGP events")

        for event in events:
            print(
                f"{event['kind']:12} | "
                f"{event['name']}"
            )

        # Don't create calendar events yet.
        return []

    def get_events(self):

        events = self.download()

        return self.parse(events)