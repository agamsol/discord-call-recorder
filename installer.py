import os
import sys
import time
import ctypes
from utilities.CustomLogger import create_logger
from utilities.recording import CoreFunctions
from win32com.client import Dispatch


log = create_logger(
    log_date_format="%d-%m-%Y %H:%M:%S",
    logs_directory="logs",
    log_level='INFO',
    logger_name="discord_call_recorder_installer",
    alias="DCR-INSTALLER"
)

core = CoreFunctions()
plugin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utilities', 'record_trigger.plugin.js')
appdata_path = os.path.join(os.getenv("APPDATA"), "discord_call_recorder")


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


def create_server(appdata_path=appdata_path):

    if not os.path.exists(appdata_path):
        os.makedirs(appdata_path)
        log.info(f"Created application data folder at: {appdata_path}")
    else:
        log.info(f"Application data folder already exists at: {appdata_path}")

    return


def add_to_startup():

    executable_path = appdata_path + "\\main.exe"
    appdata_startup = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

    shortcut_path = os.path.join(appdata_startup, "discord_call_recorder.lnk")

    try:
        shell = Dispatch('WScript.Shell')

        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = executable_path
        shortcut.WorkingDirectory = os.path.dirname(executable_path)
        shortcut.Description = "Auto-generated startup shortcut for starting the discord-call-recorder backend listener"

        shortcut.Save()

    except Exception as e:

        log.error("An error occured while saving shortcut file to startup\n" + e)

    return


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


def start_server():

    os.system("")

    pass


if __name__ == "__main__":

    core.inject_to_discord(install_builds=["stable"])

    create_server()
    install_dependencies()
    add_to_startup()

    time.sleep(10)
