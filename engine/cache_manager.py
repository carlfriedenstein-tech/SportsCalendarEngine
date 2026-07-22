from pathlib import Path
from datetime import datetime, timedelta
import json


class CacheManager:

    # ---------------------------------------------------------
    # INITIALIZE
    # ---------------------------------------------------------

    def __init__(
        self,
        sport,
    ):

        self.sport = sport

        self.cache_dir = (
            Path("cache")
            / sport
        )

        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.matches_dir = (
            self.cache_dir
            / "matches"
        )

        self.matches_dir.mkdir(
            exist_ok=True,
        )

    # ---------------------------------------------------------
    # CACHE FILES
    # ---------------------------------------------------------

    def events_file(self):

        return (
            self.cache_dir
            / "events.json"
        )

    def players_file(self):

        return (
            self.cache_dir
            / "players.json"
        )

    def matches_file(
        self,
        event_id,
    ):

        return (
            self.matches_dir
            / f"{event_id}.json"
        )

    # ---------------------------------------------------------
    # LOAD JSON
    # ---------------------------------------------------------

    def load_json(
        self,
        file_path,
    ):

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    # ---------------------------------------------------------
    # SAVE JSON
    # ---------------------------------------------------------

    def save_json(
        self,
        file_path,
        data,
    ):

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            file_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
            )

    # ---------------------------------------------------------
    # CACHE AGE
    # ---------------------------------------------------------

    def is_expired(
        self,
        file_path,
        max_age,
    ):

        file_path = Path(file_path)

        if not file_path.exists():

            return True

        modified = datetime.fromtimestamp(
            file_path.stat().st_mtime
        )

        return (
            datetime.now()
            - modified
        ) > max_age

    # ---------------------------------------------------------
    # CACHE EXPIRATION
    # ---------------------------------------------------------

    def cache_expired(
        self,
        file_path,
        refresh_after,
    ):

        return self.is_expired(
            file_path,
            refresh_after,
        )

    # ---------------------------------------------------------
    # DELETE CACHE
    # ---------------------------------------------------------

    def delete_file(
        self,
        file_path,
    ):

        file_path = Path(file_path)

        if file_path.exists():

            file_path.unlink()