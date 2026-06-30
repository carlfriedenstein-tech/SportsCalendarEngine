import os
import hashlib

from icalendar import Calendar, Event


class CalendarWriter:

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

        os.makedirs("output", exist_ok=True)

        with open(f"output/{filename}", "wb") as f:
            f.write(cal.to_ical())