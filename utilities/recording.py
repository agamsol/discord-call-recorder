import os
import json
import subprocess
from typing import Literal
from dotenv import load_dotenv
from utilities.CustomLogger import create_logger

if not os.path.exists("config.env"):

    print('ERROR: Please make sure that you have a "config.env" file available')

    input("\nPress ENTER to exit this window!")

load_dotenv("config.env")

DESKTOP_AUDIO_DEVICE = os.getenv("DESKTOP_AUDIO_DEVICE", "virtual-audio-capturer")
MICROPHONE_DEVICE = os.getenv("MICROPHONE_DEVICE")

RECORDING_EXTENSION: Literal["mkv", "mp3"] = os.getenv("RECORDING_EXTENSION", "mkv")
AUDIO_QUALITY = os.getenv("AUDIO_QUALITY", "2")
FFMPEG_EXECUTABLE_PATH = os.getenv("FFMPEG_EXECUTABLE_PATH", "ffmpeg")
ADDITIONAL_FFMPEG_OPTIONS = os.getenv("ADDITIONAL_FFMPEG_OPTIONS")
BASE_RECORDINGS_USER_PATH = os.path.join(os.environ['USERPROFILE'], os.getenv("BASE_RECORDINGS_USER_PATH"))

DISCORD_BUILDS = {
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

plugin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'record_trigger.plugin.js')
appdata_path = os.path.join(os.getenv("APPDATA"), "discord_call_recorder")

log = create_logger(
    log_date_format="%d-%m-%Y %H:%M:%S",
    logs_directory="logs",
    log_level=os.getenv("LOG_LEVEL", "DEBUG"),
    logger_name="discord_call_recorder_core_module",
    alias="RECORDER"
)


class CoreFunctions:

    def __init__(self):
        pass

    @staticmethod
    def inject_to_discord(install_builds: list = None):

        if not os.path.exists(plugin_path):

            log.error(f"Failed to find the record_trigger plugin at '{plugin_path}'")
            return

        for build_name in install_builds:

            if build_name is None or DISCORD_BUILDS.get(build_name) is None:

                log.warning(f"Skipping unknown discord build '{build_name}'")
                continue

            name = DISCORD_BUILDS[build_name]["name"]
            path = DISCORD_BUILDS[build_name]["path"]

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


class Recorder:

    def __init__(self):

        self.ongoing_recording = False
        self.processes = None

    @staticmethod
    def append_to_json(filename, data_to_append):

        data_list = []

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                if isinstance(loaded_data, list):
                    data_list = loaded_data
                else:
                    print(f"Warning: File '{filename}' contained valid JSON that was not a list. Starting a new list.")

        except FileNotFoundError:
            print(f"File '{filename}' not found. A new file will be created.")

        except json.JSONDecodeError:
            print(f"Warning: File '{filename}' is empty or contains invalid JSON. Starting a new list.")

        data_list.append(data_to_append)

        try:

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_list, f, indent=4, ensure_ascii=False)
            print(f"Successfully appended data to {filename}")

        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")

    def start_recording(self, body: dict):

        if self.ongoing_recording:
            print("Recording is already in progress.")
            return

        timestamp = body.get('timestamp')
        guild_id = body.get('server_id')
        channel_id = body.get('channel_id')
        channel_name: str = body.get('channel_name')

        output_filename = f"recording_{timestamp}-{channel_id}." + RECORDING_EXTENSION

        if guild_id == "@me":

            base_path = os.path.join(BASE_RECORDINGS_USER_PATH, "discord", "DMs", str(channel_id))
        else:
            base_path = os.path.join(BASE_RECORDINGS_USER_PATH, "discord", "guilds", str(guild_id), "channels", str(channel_id))

        os.makedirs(base_path, exist_ok=True)
        recording_path = os.path.join(base_path, output_filename)
        log.info(f"{recording_path=}")

        ffmpeg_command = [
            FFMPEG_EXECUTABLE_PATH,
            '-f', 'dshow', '-i', f'audio={MICROPHONE_DEVICE}',
            '-f', 'dshow', '-i', f'audio={DESKTOP_AUDIO_DEVICE}',
            '-filter_complex', '[0:a][1:a]amerge=inputs=2[a]',
            '-map', '[a]',
            '-vn',
            '-c:a', 'libmp3lame',
            '-q:a', AUDIO_QUALITY,
            recording_path
        ]

        if RECORDING_EXTENSION == "mkv":
            ffmpeg_command.extend(['-f', 'matroska'])

        log.info(f"""Starting to record -> Listening to devices
\tDiscord Build: {body.get('build')}
\tGuild ID: {body.get('server_id') if body.get('server_id') != "@me" else "PM Or Group DM"}
\tChannel ID: {body.get('channel_id')}
\tChannel Name: {body.get('channel_name')}
\tOutput File: {output_filename}""")

        recording_information = {
            "build": body.get('build'),
            "timestamp": timestamp,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "output_file": output_filename,
            "recording_path": recording_path
        }

        if guild_id != "@me":

            recording_information["guild_name"] = " / ".join(channel_name.split(" / ")[1:])
            recording_information["channel_name"] = channel_name.split(" / ")[0]

        self.append_to_json("discord\\recordings.json", recording_information)

        self.ongoing_recording = True

        self.process = subprocess.Popen(
            ffmpeg_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        log.info("Recording has been successfully started")
        return

    def stop_recording(self):

        if not self.ongoing_recording:
            log.warning("No recording is currently in progress.")
            return

        self.process.communicate(b'q')

        self.ongoing_recording = False
        self.process = None

        return
