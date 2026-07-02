from engine.calendar_writer import CalendarWriter
from engine.plugin_loader import PluginLoader


class SportsCalendarEngine:

    def run(self):

        loader = PluginLoader()
        plugins = loader.load_plugins()

        writer = CalendarWriter()

        all_events = []

        for plugin in plugins:

            print(f"Loading {plugin.name}...")

            events = plugin.get_events()

            writer.write(events, plugin.filename)

            all_events.extend(events)

        writer.write(all_events, "all_sports.ics")

        print(f"\nFinished! Generated {len(all_events)} events.")