from datetime import datetime

from engine.downloader import Downloader
from engine.event import SportEvent
from plugins.base_plugin import BasePlugin


class MotoGPPlugin(BasePlugin):

    EVENTS_URL = (
    "https://api.pulselive.motogp.com/"
    "motogp/v1/events?seasonYear={}"
    ) 

    EVENT_URL = (
        "https://api.pulselive.motogp.com/"
        "motogp/v1/events/{}"
    )

    GP_NAMES = {
        "LIQUI MOLY GRAND PRIX OF GERMANY": "German GP",
        "PT GRAND PRIX OF THAILAND": "Thai GP",
        "ESTRELLA GALICIA 0,0 GRAND PRIX OF BRAZIL": "Brazilian GP",
        "RED BULL GRAND PRIX OF THE UNITED STATES": "United States GP",
        "ESTRELLA GALICIA 0,0 GRAND PRIX OF SPAIN": "Spanish GP",
        "MICHELIN GRAND PRIX OF FRANCE": "French GP",
        "MICHELIN® GRAND PRIX OF FRANCE": "French GP",
        "MONSTER ENERGY GRAND PRIX OF CATALUNYA": "Catalan GP",
        "BREMBO GRAND PRIX OF ITALY": "Italian GP",
        "GRAND PRIX OF HUNGARY": "Hungarian GP",
        "MONSTER ENERGY GRAND PRIX OF CZECHIA": "Czech GP",
        "TISSOT GRAND PRIX OF THE NETHERLANDS": "Dutch GP",
        "QATAR AIRWAYS GRAND PRIX OF GREAT BRITAIN": "British GP",
        "GRAND PRIX OF ARAGON": "Aragon GP",
        "RED BULL GRAND PRIX OF SAN MARINO AND THE RIMINI RIVIERA": "San Marino GP",
        "GRAND PRIX OF AUSTRIA": "Austrian GP",
        "MOTUL GRAND PRIX OF JAPAN": "Japanese GP",
        "PERTAMINA GRAND PRIX OF INDONESIA": "Indonesian GP",
        "GRAND PRIX OF AUSTRALIA": "Australian GP",
        "PETRONAS GRAND PRIX OF MALAYSIA": "Malaysian GP",
        "QATAR AIRWAYS GRAND PRIX OF QATAR": "Qatar GP",
        "REPSOL GRAND PRIX OF PORTUGAL": "Portuguese GP",
        "MOTUL GRAND PRIX OF VALENCIA": "Valencian GP",
    }

    SESSION_NAMES = {
        "FP1": "FP1",
        "FP2": "FP2",
        "PR": "Practice",
        "Q1": "Q1",
        "Q2": "Q2",
        "SPR": "Sprint",
        "RAC": "Race",
        "WUP": "Warm Up",
    }

    def __init__(self):
        self.downloader = Downloader()

    @property
    def name(self):
        return "MotoGP"

    @property
    def filename(self):
        return "motogp.ics"

    def download_events(self, season_year):
        return self.downloader.get_json(
        self.EVENTS_URL.format(season_year)
    )

    def download_event(self, event_id):
        return self.downloader.get_json(
            self.EVENT_URL.format(event_id)
        )
        
    def clean_event_name(self, name):
        """
        Convert official MotoGP event names into compact calendar names.
        """

        return self.GP_NAMES.get(
            name.strip(),
            name.strip().title()
        )

    def clean_session_name(self, session):

        short = session.get("shortname", "")

        if short in self.SESSION_NAMES:
            return self.SESSION_NAMES[short]

        return session.get("name", "").strip()

    def format_title(self, event, session):
        """
        Build compact calendar titles.
        """

        event_name = self.clean_event_name(
            event["name"]
        )

        if event_name.endswith(" GP"):
            event_name = event_name[:-3].strip()

        session_name = self.clean_session_name(
            session
        )

        if event.get("kind") == "TEST":

            return (
                f"🧪 MGP - {event_name} - "
                f"{session_name}"
            )

        return (
            f"🏍️ MGP - {event_name} - "
            f"{session_name}"
        )

    def build_description(self, event, session):

        country = event.get(
            "additional_name",
            ""
        ).strip()

        description = [
            "MotoGP",
            "",
            f"Session: {session.get('name','')}",
            f"Country: {country}"
        ]

        laps = session.get("num_laps")

        if laps:
            description.append(
                f"Laps: {laps}"
            )

        return "\n".join(description)
        
    def parse_event(self, event):

        calendar_events = []

        is_test = event.get("kind") == "TEST"

        venue = event.get("name", "").strip()

        for session in event.get("broadcasts", []):

            category = session.get("category", {})

            # MotoGP only
            if category.get("acronym") != "MGP":
                continue

            # Skip media
            if session.get("type") == "MEDIA":
                continue

            short = session.get("shortname", "")

            # GP weekends:
            # only Sprint and Race
            if not is_test:

                if short not in ("SPR", "RAC"):
                    continue

            try:

                start = datetime.fromisoformat(
                    session["date_start"]
                )

                end = datetime.fromisoformat(
                    session["date_end"]
                )

            except Exception:

                print(
                    f"Skipping invalid session:"
                    f" {session.get('name','Unknown')}"
                )

                continue

            calendar_events.append(

                SportEvent(

                    title=self.format_title(
                        event,
                        session
                    ),

                    start=start,

                    end=end,

                    venue=venue,

                    description=self.build_description(
                        event,
                        session
                    ),

                )

            )

        return calendar_events
        
    def parse(self):

        calendar_events = []

        current_year = datetime.now().year

        season_years = [
            current_year,
            current_year + 1,
        ]

        season_events = []

        for season_year in season_years:

            print(
                f"Checking MotoGP season {season_year}..."
            )

            try:

                downloaded_events = (
                    self.download_events(
                        season_year
                    )
                )

            except Exception as ex:

                if season_year == current_year:

                    raise

                print(
                    f"MotoGP season {season_year} "
                    f"is not available yet"
                )

                print(f"  {ex}")

                continue

            print(
                f"Downloaded "
                f"{len(downloaded_events)} "
                f"MotoGP events for {season_year}"
            )

            season_events.extend(
                downloaded_events
            )

        seen_event_ids = set()

        for season_event in season_events:

            event_id = season_event.get("id")

            if not event_id:

                continue

            if event_id in seen_event_ids:

                continue

            seen_event_ids.add(event_id)

            kind = season_event.get(
                "kind",
                ""
            )

            # Ignore presentations and media-only events.
            if kind == "MEDIA":

                continue

            event_name = season_event.get(
                "name",
                ""
            ).strip()

            print(
                f"Loading {event_name}..."
            )

            try:

                event = self.download_event(
                    event_id
                )

                calendar_events.extend(
                    self.parse_event(event)
                )

            except Exception as ex:

                print(
                    f"Failed loading {event_name}"
                )

                print(f"  {ex}")

        calendar_events.sort(
            key=lambda event: event.start
        )

        if calendar_events:

            print(
                f"MotoGP calendar coverage: "
                f"{calendar_events[0].start} -> "
                f"{calendar_events[-1].end}"
            )

        else:

            print(
                "WARNING: MotoGP generated 0 events"
            )

        return calendar_events

    def get_events(self):

        return self.parse()