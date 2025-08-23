import os
import sys
import time
import ctypes
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


def request_elevation(command_line: list) -> bool:
    """
    Executes a command with administrator privileges via a UAC prompt.

    This function leverages the 'runas' verb in the Windows ShellExecuteW API
    call, which is the standard method for requesting elevation.

    Args:
        command_line: A list containing the executable path and its arguments.

    Returns:
        True if the ShellExecuteW call was successfully dispatched (return code > 32).
        False if the call failed, which can occur if the user denies the UAC
        prompt or if other system errors are encountered.
    """
    if not command_line:
        log.error("Cannot request elevation for an empty command.")
        return False

    executable = command_line[0]
    params = " ".join(command_line[1:])

    try:
        ret_code = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            executable,
            params,
            None,
            1
        )
    except Exception as e:
        log.error(f"An unexpected error occurred while calling ShellExecuteW: {e}")
        return False

    log.debug(f"ShellExecuteW returned code: {ret_code}")

    if ret_code == 55:

        log.critical("""You must restart the computer to complete the virtual-audio-capturer driver installation\notherwise recordings may not work properly.""")

    if ret_code > 32:
        log.info("Elevation request was successfully dispatched.")
        return True

    else:

        log.error(
            f"ShellExecuteW call failed with error code {ret_code}. "
            f"The user may have denied the UAC prompt."
        )
        return False


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

    installer_path = r"bin\recorder-devices-0.12.10-setup.exe"

    if not os.path.isfile(installer_path):
        log.error(f"Executable not found at the specified path: {installer_path}")
        sys.exit(1)

    command_to_run = [
        installer_path,
        "/nocancel",
        "/sp",
        "/verysilent",
        '/log="virtual-device-capturer.log"',
        "/norestart",
        "/restartexitcode=55",
        "/nocloseapplications",
    ]

    log.debug(f"Attempting to run command: {' '.join(command_to_run)}")
    log.info("Please respond to the UAC prompt on your screen.")

    if not request_elevation(command_to_run):
        log.critical("Failed to elevate the process. The command was not executed.")
        return


if __name__ == "__main__":

    inject_to_discord(install_builds=["stable", "ptb", "canary", "development"])

    install_dependencies()

    time.sleep(10)
