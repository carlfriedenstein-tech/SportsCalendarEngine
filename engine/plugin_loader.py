from plugins.fifa_world_cup import FIFAWorldCupPlugin
from plugins.motogp import MotoGPPlugin
from plugins.worldsbk import WorldSBKPlugin
from plugins.proteas import ProteasPlugin
from plugins.springboks import SpringboksPlugin


class PluginLoader:

    def load_plugins(self):

        return [

            FIFAWorldCupPlugin(),

            MotoGPPlugin(),

            WorldSBKPlugin(),

            ProteasPlugin(),

            SpringboksPlugin()

        ]