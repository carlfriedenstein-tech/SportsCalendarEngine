from plugins.fifa_world_cup import FIFAWorldCupPlugin
from plugins.motogp import MotoGPPlugin


class PluginLoader:

    def load_plugins(self):

        return [

            FIFAWorldCupPlugin(),
            MotoGPPlugin(),

        ]