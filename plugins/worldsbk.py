from datetime import datetime, timedelta

from engine.downloader import Downloader
from engine.event import SportEvent
from plugins.base_plugin import BasePlugin


class WorldSBKPlugin(BasePlugin):

    ROUNDS_URL = (
        "https://api.wsbk.pulselive.com/"
        "wsbk-events/v1/seasons/2026/rounds"
    )

    SESSIONS_URL = (
        "https://api.wsbk.pulselive.com/"
        "wsbk-events/v1/seasons/2026/rounds/{}/sessions"
    )

    SESSION_NAMES = {
        "SP": "Superpole",
        "RC1": "Race 1",
        "SPRC": "Superpole Race",
        "RC2": "Race 2",
    }

    SESSION_LENGTHS = {
        "SP": 60,
        "RC1": 60,
        "SPRC": 30,
        "RC2": 60,
    }
    CIRCUIT_NAMES = {
        "Phillip Island Grand Prix Circuit": "Phillip Island",
        "MotorLand Aragon": "Aragon",
        "Autódromo Internacional do Algarve": "Portimão",
        "Circuit de Nevers Magny-Cours": "Magny-Cours",
        "Circuito de Jerez - Ángel Nieto": "Jerez",
        "TT Circuit Assen": "Assen",
        "Misano Circuit Sic 58": "Misano",
        "Donington Park Circuit": "Donington",
        "Autodrom Most": "Most",
        "Circuito Estoril": "Estoril",
        "Cremona Circuit": "Cremona",
        "Balaton Park Circuit": "Balaton Park",
    }

    def __init__(self):
        self.downloader = Downloader()

    @property
    def name(self):
        return "WorldSBK"

    @property
    def filename(self):
        return "worldsbk.ics"

    def download_rounds(self):
        return self.downloader.get_json(
            self.ROUNDS_URL
        )

    def download_sessions(self, round_id):
        return self.downloader.get_json(
            self.SESSIONS_URL.format(round_id)
        )

    def clean_session_name(self, session):

        attributes = session.get(
            "attributes",
            {}
        )

        short = attributes.get(
            "short_name",
            ""
        )

        return self.SESSION_NAMES.get(
            short,
            attributes.get(
                "brief_description",
                attributes.get(
                    "description",
                    short
                )
            )
        )

    def format_title(self, circuit, session):

        return (
            f"🏍 WSBK - "
            f"{circuit} - "
            f"{self.clean_session_name(session)}"
        )

    def build_description(
        self,
        round_data,
        session
    ):

        round_attributes = round_data.get(
            "attributes",
            {}
        )

        circuit = self.CIRCUIT_NAMES.get(
            round_attributes.get(
                "name",
                "Unknown Circuit"
            ),
            round_attributes.get(
                "name",
                "Unknown Circuit"
            )
        )

        country = round_attributes.get(
            "country_iso",
            ""
        )

        return "\n".join([
            "WorldSBK",
            "",
            f"Session: {self.clean_session_name(session)}",
            f"Circuit: {circuit}",
            f"Country: {country}"
        ])

    def build_event(
        self,
        round_data,
        session
    ):

        round_attributes = round_data.get(
            "attributes",
            {}
        )

        session_attributes = session.get(
            "attributes",
            {}
        )

        short = session_attributes.get(
            "short_name",
            ""
        )

        if short not in self.SESSION_NAMES:
            return None

        start_text = session_attributes.get(
            "start_date_utc"
        )

        if not start_text:
            return None

        start = datetime.fromisoformat(
            start_text
        )

        duration = self.SESSION_LENGTHS.get(
            short,
            60
        )

        end = start + timedelta(
            minutes=duration
        )

        circuit = self.CIRCUIT_NAMES.get(
            round_attributes.get(
                "name",
                "Unknown Circuit"
            ),
            round_attributes.get(
                "name",
                "Unknown Circuit"
            )
        )

        return SportEvent(

            title=self.format_title(
                circuit,
                session
            ),

            start=start,

            end=end,

            venue=circuit,

            description=self.build_description(
                round_data,
                session
            ),

        )

    def parse_round(
        self,
        round_data
    ):

        calendar_events = []

        round_id = round_data.get(
            "attributes",
            {}
        ).get(
            "source_id"
        )

        if not round_id:
            return calendar_events

        print(
            f"Loading {round_data['attributes']['name']}..."
        )

        sessions = self.download_sessions(
            round_id
        )

        for session in sessions.get(
            "data",
            []
        ):

            category = (
                session.get(
                    "relationships",
                    {}
                )
                .get(
                    "category",
                    {}
                )
                .get(
                    "data",
                    {}
                )
                .get(
                    "id",
                    ""
                )
            )

            if category != "SBK":
                continue

            event = self.build_event(
                round_data,
                session
            )

            if event is not None:

                calendar_events.append(
                    event
                )

        calendar_events.sort(
            key=lambda e: e.start
        )

        return calendar_events

    def parse(self):

        calendar_events = []

        rounds = self.download_rounds()

        season_rounds = rounds.get(
            "data",
            []
        )

        print(
            f"Downloaded {len(season_rounds)} WorldSBK rounds"
        )

        for round_data in season_rounds:

            try:

                calendar_events.extend(

                    self.parse_round(
                        round_data
                    )

                )

            except Exception as ex:

                print(
                    f"Failed loading "
                    f"{round_data['attributes']['name']}"
                )

                print(
                    f"  {ex}"
                )

        return calendar_events

    def get_events(self):

        return self.parse()                