from plugins.fifa_world_cup import FIFAWorldCupPlugin
from plugins.motogp import MotoGPPlugin
from plugins.worldsbk import WorldSBKPlugin


class PluginLoader:

    def load_plugins(self):

        return [

            FIFAWorldCupPlugin(),
            MotoGPPlugin(),
            WorldSBKPlugin()
        ]