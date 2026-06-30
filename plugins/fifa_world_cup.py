import json
from datetime import datetime

from engine.event import SportEvent
from plugins.base_plugin import BasePlugin


class FIFAWorldCupPlugin(BasePlugin):

    @property
    def name(self):
        return "FIFA World Cup"

    def get_events(self):

        events = []

        with open("data/fifa_world_cup.json", "r", encoding="utf-8") as f:
            matches = json.load(f)

        for match in matches:

            events.append(
                SportEvent(
                    title=match["title"],
                    start=datetime.fromisoformat(match["start"]),
                    end=datetime.fromisoformat(match["end"]),
                    venue=match["venue"],
                    description=match["description"]
                )
            )

        return events