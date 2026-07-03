from datetime import datetime, timedelta

from engine.downloader import Downloader
from engine.event import SportEvent
from plugins.base_plugin import BasePlugin


class SpringboksPlugin(BasePlugin):

    URL = (
        "https://springboks.rugby/"
        "api/match-centre/matches"
        "?startDate=2025-01-01"
        "&endDate=2030-12-31T23:59:59"
        "&pageIndex=0"
        "&pageSize=100"
        "&IsAscending=true"
        "&teamOneId=e976cfc2-f80b-4c1a-8472-838cd54f0fbc"
    )

    def __init__(self):

        self.downloader = Downloader()

    @property
    def name(self):

        return "Springboks"

    @property
    def filename(self):

        return "springboks.ics"

    def download_matches(self):

        print(
            "Downloading Springboks fixtures..."
        )

        return self.downloader.get_json(
            self.URL
        )

    def get_match_title(
        self,
        match
    ):

        springboks = None
        opponent = None

        for team in match.get(
            "teams",
            []
        ):

            if team["name"] == "Springboks":

                springboks = team

            else:

                opponent = team

        if (
            springboks is None
            or opponent is None
        ):

            return (
                "Springboks",
                "Unknown"
            )

        if springboks.get(
            "isHomeTeam",
            False
        ):

            title = (
                f"Springboks vs "
                f"{opponent['name']}"
            )

        else:

            title = (
                f"{opponent['name']} vs "
                f"Springboks"
            )

        return (
            title,
            opponent["name"]
        )
    
    def parse(self):

        events = []

        matches = self.download_matches()

        if isinstance(
            matches,
            dict
        ):

            matches = matches.get(
                "matches",
                matches.get(
                    "items",
                    []
                )
            )

        print(
            f"Downloaded {len(matches)} matches"
        )

        for match in matches:

            if match.get(
                "isCancelled",
                False
            ):

                continue

            match_title, opponent = (
    self.get_match_title(
        match
    )
)

            start = datetime.fromisoformat(
                match["utcDate"]
            )

            end = start + timedelta(
                hours=3
            )

            competition = match.get(
                "competitionName",
                ""
            )

            venue = match.get(
                "venueName",
                ""
            )

            round_name = match.get(
                "roundName",
                ""
            )

            title = "\n".join([

                "🏉 Springboks",

                match_title,

                competition

            ])

            description = "\n".join([

                "Springboks",

                "",

                f"Competition: {competition}",

                f"Round: {round_name}",

                f"Opponent: {opponent}",

                f"Venue: {venue}"

            ])

            events.append(

                SportEvent(

                    title=title,

                    start=start,

                    end=end,

                    venue=venue,

                    description=description

                )

            )

        events.sort(
            key=lambda e: e.start
        )

        print(
            f"Generated {len(events)} Springboks events"
        )

        return events
    
    def get_events(self):

        return self.parse()