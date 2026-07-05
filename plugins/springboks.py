from datetime import datetime, timedelta, timezone

from engine.downloader import Downloader
from engine.event import SportEvent
from plugins.base_plugin import BasePlugin


class SpringboksPlugin(BasePlugin):

    URL = (
        "https://springboks.rugby/"
        "api/match-centre/matches"
        "?startDate={}"
        "&endDate={}"
        "&pageIndex={}"
        "&pageSize={}"
        "&IsAscending=true"
    )

    PAGE_SIZE = 100
    FUTURE_YEARS = 10

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

        current_year = datetime.now().year

        start_date = (
            f"{current_year}-01-01"
        )

        end_date = (
            f"{current_year + self.FUTURE_YEARS}"
            "-12-31T23:59:59"
        )

        matches = []

        seen_matches = set()

        page_index = 0

        max_pages = 100

        while True:

            if page_index >= max_pages:

                print(
                    "WARNING: Springboks pagination "
                    "reached safety limit"
                )

                break

            print(
                f"Downloading Springboks page "
                f"{page_index}..."
            )

            url = self.URL.format(
                start_date,
                end_date,
                page_index,
                self.PAGE_SIZE
            )

            response = self.downloader.get_json(
                url
            )

            if isinstance(response, dict):

                page_matches = response.get(
                    "matches",
                    response.get(
                        "items",
                        []
                    )
                )

            elif isinstance(response, list):

                page_matches = response

            else:

                page_matches = []

            print(
                f"Downloaded "
                f"{len(page_matches)} matches "
                f"from page {page_index}"
            )

            for match in page_matches:

                match_id = match.get(
                    "id"
                )

                if match_id is not None:

                    key = (
                        "id",
                        match_id,
                    )

                else:

                    key = (
                        match.get(
                            "utcDate",
                            ""
                        ),
                        tuple(
                            sorted(
                                team.get(
                                    "name",
                                    ""
                                )
                                for team
                                in match.get(
                                    "teams",
                                    []
                                )
                            )
                        ),
                    )

                if key in seen_matches:

                    continue

                seen_matches.add(
                    key
                )

                matches.append(
                    match
                )

            if len(page_matches) < self.PAGE_SIZE:

                break

            page_index += 1

        matches.sort(
            key=lambda match: match.get(
                "utcDate",
                ""
            )
        )

        print(
            f"Downloaded "
            f"{len(matches)} unique "
            f"Springboks matches"
        )

        return matches

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

        try:

            matches = self.download_matches()

        except Exception as ex:

            print(
                "ERROR: Failed downloading "
                "Springboks fixtures"
            )

            print(
                f"  {ex}"
            )

            return events

        print(
            f"Downloaded {len(matches)} matches"
        )

        springbok_matches = 0

        cancelled_matches = 0

        failed_matches = 0

        for match in matches:

            if not any(
                team.get(
                    "name"
                ) == "Springboks"
                for team in match.get(
                    "teams",
                    []
                )
            ):

                continue

            springbok_matches += 1

            if match.get(
                "isCancelled",
                False
            ):

                cancelled_matches += 1

                continue

            try:

                match_title, opponent = (
                    self.get_match_title(
                        match
                    )
                )

                start = datetime.fromisoformat(
                    match["utcDate"]
                ).replace(
                    tzinfo=timezone.utc
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

                    f"🏉 {match_title}",

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

            except Exception as ex:

                failed_matches += 1

                print(
                    "Failed parsing Springboks "
                    "match"
                )

                print(
                    f"  {ex}"
                )

        events.sort(
            key=lambda event: event.start
        )

        print(
            f"Found {springbok_matches} "
            f"Springboks matches"
        )

        if cancelled_matches:

            print(
                f"Skipped {cancelled_matches} "
                f"cancelled Springboks matches"
            )

        if failed_matches:

            print(
                f"WARNING: {failed_matches} "
                f"Springboks matches failed parsing"
            )

        print(
            f"Generated {len(events)} "
            f"Springboks events"
        )

        if events:

            print(
                f"Springboks calendar coverage: "
                f"{events[0].start} -> "
                f"{events[-1].end}"
            )

        else:

            print(
                "WARNING: Springboks generated "
                "0 events"
            )

        return events
    
    def get_events(self):

        return self.parse()