import os
import subprocess
from utilities.CustomLogger import create_logger

log = create_logger(
    log_date_format="%d-%m-%Y %H:%M:%S",
    logs_directory="logs",
    log_level='INFO',
    logger_name="discord_call_recorder_installer",
    alias="DCR-INSTALLER"
)

plugin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utilities', 'record_trigger.plugin.js')

discord_builds = {
    "stable": {
        "name": "Stable Discord",
        "path": os.path.join(os.getenv("LOCALAPPDATA"), "Discord"),
        "executable": "Discord.exe"
    },
    "ptb": {
        "name": "Discord Ptb",
        "path": os.path.join(os.getenv("LOCALAPPDATA"), "DiscordPTB"),
        "executable": "DiscordPTB.exe"
    },
    "canary": {
        "name": "Discord Canary",
        "path": os.path.join(os.getenv("LOCALAPPDATA"), "DiscordCanary"),
        "executable": "DiscordCanary.exe"
    }
}


def inject_to_discord(install_builds: list = None):

    if not os.path.exists(plugin_path):

        log.error(f"Failed to find the record_trigger plugin at '{plugin_path}'")
        return

    for build_name in install_builds:

        if build_name is None or discord_builds.get(build_name) is None:

            log.warning(f"Skipping unknown discord build '{build_name}'")

            continue

        name = discord_builds[build_name]["name"]
        path = discord_builds[build_name]["path"]

        log.debug(f"* ({name}) You requested to inject  . . .")

        folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

        for folder in folders:

            if not folder.startswith("app-"):
                continue

            full_injection_path = os.path.join(path, folder, 'modules', 'discord_desktop_core-1', 'discord_desktop_core', 'index.js')

            if os.path.exists(full_injection_path):

                log.info(f"({name}) Injecting call recorder")
                log.debug(f"({name}) Full injection path: {full_injection_path}")

                content = f"""require('{plugin_path.replace("\\", "\\\\")}')\n\nmodule.exports = require('./core.asar');"""

                with open(full_injection_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                log.info(f"({name}) Successfully injected call recorder.")

            else:

                log.error(f"({name}) Failed to find a proper installation at {full_injection_path}")

    log.info("Injecttion process completed")

    return

# 2. Add to startup
def add_to_startup():
    pass

# 3. Install dependencies and drivers
def install_dependencies():

    status_code = subprocess.run()

if __name__ == "__main__":

    inject_to_discord(install_builds=["stable", "ptb", "canary", "development"])

    pass