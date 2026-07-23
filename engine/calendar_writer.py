import os
import hashlib

from icalendar import Calendar, Event


class CalendarWriter:

    OUTPUT_FOLDER = "docs"

    def write(self, events, filename):

        cal = Calendar()
        cal.add("prodid", "-//Sports Calendar Engine//")
        cal.add("version", "2.0")

        for e in events:

            event = Event()

            event.add("summary", e.title)
            event.add("dtstart", e.start)
            event.add("dtend", e.end)
            event.add("location", e.venue)
            event.add("description", e.description)

            uid = hashlib.md5(
                f"{e.title}{e.start}{e.venue}".encode("utf-8")
            ).hexdigest()

            event.add("uid", uid)

            cal.add_component(event)

        os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)

        output_file = os.path.join(
            self.OUTPUT_FOLDER,
            filename
        )

        calendar_data = cal.to_ical()

        if os.path.exists(output_file):
            with open(output_file, "rb") as f:
                if f.read() == calendar_data:
                    print(f"  No changes: {output_file}")
                    return

        with open(output_file, "wb") as f:
            f.write(calendar_data)

        print(f"  Updated: {output_file}")