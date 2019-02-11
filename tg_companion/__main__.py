import asyncio
import importlib
import re

from tg_companion import LOGGER, TO_INSTALL, proxy
from tg_companion.modules import MODULES
from tg_companion.plugins import PLUGINS, PluginManager
from tg_companion.tgclient import client

for module_name in MODULES:
    imported_module = importlib.import_module(
        "tg_companion.modules." + module_name)

for plugin_name in PLUGINS:
    imported_plugin = importlib.import_module(
        "tg_companion.plugins." + plugin_name)

if proxy:
    LOGGER.info(f"Connecting to Telegram over proxy: {proxy[1]}:{proxy[2]}")
    LOGGER.info("Use .ping in any chat to see if your userbot has connected.")
else:
    LOGGER.info("Your userbot is running. Type .ping in any chat to test it")


loop = asyncio.get_event_loop()


if __name__ == "__main__":

    if TO_INSTALL:
        to_match = re.match(
            r"([^\/]+)\/([^\/]+)(\/([^\/]+)(\/(.*))?)?",
            TO_INSTALL)
        if to_match:
            loop.run_until_complete(
                PluginManager.download_plugins(
                    user=to_match.group(1),
                    repo=to_match.group(2),
                    plugin=to_match.group(4)))
        else:
            loop.run_until_complete(
                PluginManager.download_plugins(
                    plugin=TO_INSTALL))
    client.run_until_disconnected()
