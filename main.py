import os
import json
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, request, send_from_directory
from utilities.recording import Recorder
from utilities.CustomLogger import create_logger

load_dotenv()

MEDIA_FOLDER = os.getenv("MEDIA_FOLDER", "discord")

DESKTOP_AUDIO_DEVICE = os.getenv("DESKTOP_AUDIO_DEVICE", "virtual-audio-capturer")
MICROPHONE_DEVICE = os.getenv("MICROPHONE_DEVICE")

DISCORD_BUILDS = os.getenv("DISCORD_BUILDS", "stable, ptb, canary")

FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 49151))

log = create_logger(
    log_date_format="%d-%m-%Y %H:%M:%S",
    logs_directory="logs",
    log_level=os.getenv("LOG_LEVEL", "DEBUG"),
    logger_name="discord_call_recorder_server",
    alias="FLASK"
)

app = Flask(__name__)
CORS(app)
discord_stable = Recorder()
discord_ptb = Recorder()
discord_canary = Recorder()


@app.before_request
def allow_cors_requests():

    if request.method == 'OPTIONS':
        return "OK", 200


@app.route("/recordings", methods=["GET"])
def get_recordings():

    try:
        with open("discord\\recordings.json", "r", encoding="utf-8") as f:
            recordings = json.load(f)
        return recordings, 200
    except FileNotFoundError:
        return {"message": "No recordings found."}, 404


@app.route("/recording/<path:filename>", methods=["GET", "DELETE"])
def request_recording(filename):

    if request.method == 'DELETE':

        file_path = "discord\\recordings.json"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                recordings = json.load(f)

            updated_recordings = [rec for rec in recordings if rec.get("recording_path") != filename]

            if len(updated_recordings) < len(recordings):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(updated_recordings, f, indent=4, ensure_ascii=False)

                log.info(f"Successfully removed object with recording path '{filename}' from {file_path}")
            else:
                print(f"Notice: No object found with recording path '{filename}'. The file was not modified.")

        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from the file '{file_path}'. Ensure it is a valid JSON document.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        try:
            os.remove(os.path.join(MEDIA_FOLDER, filename))

        except FileNotFoundError:
            return {"message": "Recording not found."}, 404

        return {"message": "Recording deleted successfully."}, 200

    return send_from_directory(MEDIA_FOLDER, filename)


@app.route("/join", methods=["POST", "OPTIONS"])
def flask_join():

    body = request.get_json()

    build_type = body.get("build")

    match build_type:

        case "stable":

            discord_stable.start_recording(body)
            return 'OK', 200

        case "ptb":

            discord_ptb.start_recording(body)
            return 'OK', 200

        case "canary":

            discord_canary.start_recording(body)
            return 'OK', 200

    return 'INVALID_BUILD_SPECIFIED', 400


@app.route("/leave", methods=["POST", "OPTIONS"])
def flask_leave():

    body = request.get_json()
    build_type = body.get("build")

    match build_type:

        case "stable":

            discord_stable.stop_recording()
            return 'OK', 200

        case "ptb":

            discord_ptb.stop_recording()
            return 'OK', 200

        case "canary":

            discord_canary.stop_recording()
            return 'OK', 200

    return 'INVALID_BUILD_SPECIFIED', 400


if __name__ == "__main__":

    log.info(f"Starting Flask app on {FLASK_HOST}:{FLASK_PORT}\n\tDevices that will be recorded are ->\n\tMicrophone: {MICROPHONE_DEVICE}\n\tDesktop Audio: {DESKTOP_AUDIO_DEVICE}")
    app.run(host="0.0.0.0", port=49151)
