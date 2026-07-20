from pathlib import Path


class CalendarGuard:

    CALENDAR_FOLDER = Path("docs")

    @classmethod
    def should_write(
        cls,
        plugin_name,
        filename,
        validation
    ):

        filepath = cls.CALENDAR_FOLDER / filename

        # No valid events
        if not validation.events:

            if filepath.exists():

                print(
                    f"WARNING: {plugin_name} returned no valid events."
                )

                print(
                    f"Keeping existing calendar: {filename}"
                )

                return False

            print(
                f"WARNING: {plugin_name} returned no valid events "
                "and no existing calendar was found."
            )

            return False

        return True