from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
from werkzeug.exceptions import HTTPException

import config
import tts

app = Flask(__name__)
CORS(app, resources={r"/v1/audio/speech": {"origins": config.CORS_ALLOWED_ORIGIN}})
CORS(
    app, resources={r"/get_predefined_voices": {"origins": config.CORS_ALLOWED_ORIGIN}}
)


@app.route("/v1/audio/speech", methods=["POST"])
def speech_api():
    data = request.get_json()

    # Extract parameters from the request
    text = data.get("input")
    voice = data.get("voice")
    speed = data.get("speed", 1.0)
    cfg = data.get("cfg_weight", config.AUDIO_CFG_WEIGHT)
    temperature = data.get("temperature", config.AUDIO_TEMPERATURE)
    exaggeration = data.get("exaggeration", config.AUDIO_EXAGGERATION)
    response_format = data.get("response_format", "wav")
    seed = data.get("seed", config.SEED)

    print(f"Got request: {data}")
    chunk_size = data.get("chunk_size", 250)

    # Validate parameters
    if not text:
        return (
            jsonify({"error": "Input text is required."}),
            400,
        )
    if voice not in config.SUPPORTED_VOICES:
        return jsonify({"error": "Unsupported voice specified."}), 400
    if response_format not in config.SUPPORTED_RESPONSE_FORMATS:
        return (
            jsonify(
                {
                    "error": "Unsupported response format specified. Got: "
                    + response_format
                }
            ),
            400,
        )

    if chunk_size < 1:
        return jsonify({"error": "Chunk size must be greater than 0."}), 400

    # Generate audio from the text
    audio_data = tts.generate_audio(
        text, voice, speed, cfg, temperature, exaggeration, chunk_size, seed
    )

    # Convert the audio data to the desired format
    converted_audio_data = tts.convert_audio_format(audio_data, response_format)

    # Create a BytesIO object for the response
    audio_io = io.BytesIO(converted_audio_data)
    audio_io.seek(0)

    # Set the appropriate MIME type based on the requested response format
    mime_type = "audio/" + response_format

    return send_file(
        audio_io,
        mimetype=mime_type,
        as_attachment=True,
        download_name=f"speech.{response_format}",
    )


@app.route("/tts", methods=["POST"])
def tts_api():
    data = request.get_json()

    # Extract parameters from the request
    text = data.get("text")
    voice = data.get("predefined_voice_id")
    speed = data.get("speed", 1.0)
    cfg = data.get("cfg_weight", config.AUDIO_CFG_WEIGHT)
    temperature = data.get("temperature", config.AUDIO_TEMPERATURE)
    exaggeration = data.get("exaggeration", config.AUDIO_EXAGGERATION)
    response_format = data.get("output_format", "wav")
    seed = data.get("seed", config.SEED)

    print(f"Got request: {data}")
    chunk_size = data.get("chunk_size", 250)

    # Validate parameters
    if not text:
        return (
            jsonify({"error": "Input text is required."}),
            400,
        )
    if voice not in config.SUPPORTED_VOICES:
        return jsonify({"error": "Unsupported voice specified."}), 400
    if response_format not in config.SUPPORTED_RESPONSE_FORMATS:
        return (
            jsonify(
                {
                    "error": "Unsupported response format specified. Got: "
                    + response_format
                }
            ),
            400,
        )

    if chunk_size < 1:
        return jsonify({"error": "Chunk size must be greater than 0."}), 400

    # Generate audio from the text
    audio_data = tts.generate_audio(
        text, voice, speed, cfg, temperature, exaggeration, chunk_size, seed
    )

    # Convert the audio data to the desired format
    converted_audio_data = tts.convert_audio_format(audio_data, response_format)

    # Create a BytesIO object for the response
    audio_io = io.BytesIO(converted_audio_data)
    audio_io.seek(0)

    # Set the appropriate MIME type based on the requested response format
    mime_type = "audio/" + response_format

    return send_file(
        audio_io,
        mimetype=mime_type,
        as_attachment=True,
        download_name=f"speech.{response_format}",
    )


# add a /voices endpoint that returns the supported voices
@app.route("/voices", methods=["GET"])
def get_voices_api():
    return jsonify({"voices": config.SUPPORTED_VOICES})


@app.get("/get_predefined_voices")
def get_predefined_voices_api():
    """Returns a list of predefined voices with display names and filenames."""
    """List of dictionaries: [{"display_name": "Formatted Name", "filename": "original_file.wav"}, ...]"""
    try:
        response = jsonify(
            [
                {"display_name": voice, "filename": voice}
                for voice in config.SUPPORTED_VOICES
            ]
        )
        return response

    except Exception:
        raise HTTPException(
            status_code=500, detail="Failed to retrieve predefined voices list."
        )


@app.post("/save")
def save_api():
    # do nothing
    return "{}"
