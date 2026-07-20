from plugins.base_plugin import BasePlugin

from plugins.fifa_world_cup import FIFAWorldCupPlugin
from plugins.motogp import MotoGPPlugin
from plugins.worldsbk import WorldSBKPlugin
from plugins.proteas import ProteasPlugin
from plugins.springboks import SpringboksPlugin
from plugins.motoamerica import MotoAmericaPlugin


class PluginLoader:

    def load_plugins(self):

        plugins = [

            FIFAWorldCupPlugin(),

            MotoGPPlugin(),

            WorldSBKPlugin(),

            ProteasPlugin(),

            SpringboksPlugin(),

            MotoAmericaPlugin(),

        ]

        plugin_names = set()
        filenames = set()

        valid_plugins = []

        for plugin in plugins:

            if not isinstance(plugin, BasePlugin):
                raise TypeError(
                    f"{plugin.__class__.__name__} must inherit from BasePlugin."
                )

            if not plugin.enabled:
                print(f"Skipping disabled plugin: {plugin.name}")
                continue

            if plugin.name in plugin_names:
                raise ValueError(
                    f"Duplicate plugin name: {plugin.name}"
                )

            plugin_names.add(plugin.name)

            if plugin.filename in filenames:
                raise ValueError(
                    f"Duplicate calendar filename: {plugin.filename}"
                )

            filenames.add(plugin.filename)

            valid_plugins.append(plugin)

        valid_plugins.sort(key=lambda p: p.name)

        return valid_plugins