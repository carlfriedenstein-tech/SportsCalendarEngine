from datetime import datetime, timedelta

from engine.downloader import Downloader
from engine.event import SportEvent
from plugins.base_plugin import BasePlugin


class FIFAWorldCupPlugin(BasePlugin):

    URL = "https://api.fifa.com/api/v3/calendar/matches?language=en&count=500&idSeason=285023"

    @property
    def name(self):
        return "FIFA World Cup"

    @property
    def filename(self):
        return "fifa_world_cup.ics"

    def download(self):
        downloader = Downloader()
        return downloader.get_json(self.URL)

    def get_description(self, items, default=""):
        if items and len(items) > 0:
            return items[0].get("Description", default)
        return default

    def parse(self, data):

        events = []

        for match in data["Results"]:

            # Home team
            if match.get("Home") and match["Home"] and match["Home"].get("TeamName"):
                home = self.get_description(match["Home"]["TeamName"], "TBD")
            else:
                home = match.get("PlaceHolderA", "TBD")

            # Away team
            if match.get("Away") and match["Away"] and match["Away"].get("TeamName"):
                away = self.get_description(match["Away"]["TeamName"], "TBD")
            else:
                away = match.get("PlaceHolderB", "TBD")

            stadium = self.get_description(
                match.get("Stadium", {}).get("Name"),
                "Unknown Stadium"
            )

            city = self.get_description(
                match.get("Stadium", {}).get("CityName"),
                ""
            )

            start = datetime.fromisoformat(
                match["Date"].replace("Z", "+00:00")
            )

            end = start + timedelta(hours=2)

            stage = self.get_description(
                match.get("StageName"),
                "Unknown Stage"
            )

            group = self.get_description(
                match.get("GroupName"),
                ""
            )

            description = stage
            if group:
                description += f" - {group}"

            venue = stadium
            if city:
                venue += f", {city}"

            events.append(
                SportEvent(
                    title=f"⚽ FIFA World Cup\n{home} vs {away}",
                    start=start,
                    end=end,
                    venue=venue,
                    description=description,
                )
            )

        return events

    def get_events(self):

        data = self.download()

        return self.parse(data)