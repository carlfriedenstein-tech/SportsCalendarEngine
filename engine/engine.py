from engine.calendar_writer import CalendarWriter
from engine.plugin_loader import PluginLoader


class SportsCalendarEngine:

    def run(self):

        loader = PluginLoader()

        plugins = loader.load_plugins()

        events = []

        for plugin in plugins:

            print(f"Loading {plugin.name}...")

            events.extend(plugin.get_events())

        writer = CalendarWriter()

        writer.write(events, "master.ics")

        print(f"\nFinished! Generated {len(events)} events.")