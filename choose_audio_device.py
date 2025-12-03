import os
import dotenv
import subprocess
from typing import Literal

if not os.path.exists("config.env"):

    print('ERROR: Please make sure that you have a "config.env" file available')

    input("\nPress ENTER to exit this window!")

DOTENV_FILE = "config.env"

dotenv.load_dotenv(DOTENV_FILE)

FFMPEG_EXECUTABLE_PATH = os.getenv("FFMPEG_EXECUTABLE_PATH", "ffmpeg")
ADDITIONAL_FFMPEG_OPTIONS = os.getenv("ADDITIONAL_FFMPEG_OPTIONS")


def get_available_devices():

    ffmpeg_command = [
        FFMPEG_EXECUTABLE_PATH,
        '-list_devices', 'true', '-f', 'dshow',
        '-i', 'dummy', ADDITIONAL_FFMPEG_OPTIONS
    ]

    process = subprocess.Popen(
        ffmpeg_command,
        stderr=subprocess.PIPE,
        text=True
    )

    return process


def show_devices() -> list[str]:

    process = get_available_devices()

    i = 1
    options = []

    for line in process.stderr:

        if line.endswith("(audio)\n"):

            device = line.split('\"')[1]

            print(f"{i} --> {device}")

            i += 1
            options.append(device)

    return options


def save_env_key(new_device: str) -> None:

    dotenv.set_key(
        DOTENV_FILE,
        key_to_set="MICROPHONE_DEVICE",
        value_to_set=new_device,  # options[device_selected - 1]
    )


def main() -> Literal["FAILED", "OK"]:

    device_selected = None
    devices_list = show_devices()

    try:

        device_selected = int(input("Choose a device by its presenting number: "))

    except Exception:
        pass

    if not isinstance(device_selected, int):

        print("You must specify a number that represents the device you want to choose!")
        input("Press ENTER to exit.")

        return "FAILED"

    try:

        print(f"Device Selected: {devices_list[device_selected - 1]}")

    except Exception:

        print("Device Specified not found!")
        input("Press ENTER to exit.")

        return "FAILED"

    save_env_key(devices_list[device_selected - 1])

    print("The device has been saved to the configuration!")
    input("\nPress ENTER to exit.")

    return "OK"


if __name__ == "__main__":

    response = None

    while True:

        response = main()

        if response == "OK":
            break
