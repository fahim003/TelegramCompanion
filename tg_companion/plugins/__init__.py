from tg_companion import LOGGER
from os.path import dirname, basename, isfile
import glob
import aiohttp
import asyncio
import re


class PluginManager:
    def load_plugins():

        path = glob.glob(dirname(__file__) + "/*.py")

        plugins = [
            basename(plugin)[:-3]
            for plugin in path
            if isfile(plugin) and plugin.endswith(".py") and not plugin.endswith("__init__.py")
        ]
        return plugins

    def load_plugins_info():
        path = glob.glob(dirname(__file__) + "/*.plugin")
        plugin_dct = {}

        for plugin in path:
            if isfile(plugin) and plugin.endswith(".plugin"):
                with open(plugin) as config_file:
                    for line in config_file.read().splitlines():
                        if "Module" in line:
                            module_name = line.split("Module = ")[1]
                        item = line.split("=")[0]
                        val = line.split("=")[1]

                        if module_name not in plugin_dct.keys():
                            plugin_dct[module_name] = {item: val}
                        if val not in plugin_dct:
                            plugin_dct[module_name].update({item: val})

        return plugin_dct

    async def download_plugins(user="nitanmarcel", repo="TgCompanionPlugins", plugin=None):
        if plugin is None:
            LOGGER.error("No plugin specified")
            return

        LOGGER.info(f"Downloading Plugin: {plugin}")

        github = f"https://api.github.com/repos/{user}/{repo}/contents/{plugin}/{plugin}"
        requirements = None

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{github}.py") as request:

                if request.status == 404:
                    LOGGER.error(f"Can't find the py file of {plugin} plugin")
                    return
                result = await request.json()

            async with session.get(result.get("download_url")) as pyfile:

                text = await pyfile.text(encoding="utf8")
                LOGGER.info("Writing python module")
                with open(f"tg_companion/plugins/{plugin}.py", "w+") as file:

                    file.write(text)

            async with session.get(f"{github}.plugin") as request:

                if request.status == 404:
                    LOGGER.error(
                        f"Can't find the plugin file of {plugin} plugin")
                    return

                result = await request.json()
            async with session.get(result.get("download_url")) as plugfile:

                text = await plugfile.text(encoding="utf8")

                LOGGER.info("Writing plugin file")

                with open(f"tg_companion/plugins/{plugin}.plugin", "w+") as file:
                    file.write(text)

            get_req = re.search("Requirements = (.+)", text)
            if get_req:
                requirements = get_req.group(1)

                if "," in requirements:
                    requirements = requirements.replace(",", "")

                LOGGER.info("Installing Requirements:")

                process = await asyncio.create_subprocess_shell(f"pip3 install {requirements}", stdin=asyncio.subprocess.PIPE)

                stdout, stderr = await process.communicate()

                LOGGER.info(f"Installed {plugin}")
                LOGGER.info(f"Plugin {plugin} Installed")

                LOGGER.info(
                    f"Please restart the companion to load the new installed plugins")


PLUGINS = sorted(PluginManager.load_plugins())

for plugin_name in PLUGINS:
    LOGGER.info(f"Loading Plugin: {plugin_name}")
__all__ = PLUGINS + ["PLUGINS"]
