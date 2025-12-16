from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
from werkzeug.exceptions import HTTPException

import config
import tts

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": config.CORS_ALLOWED_ORIGIN}})


@app.route("/v1/audio/speech", methods=["POST"])
def speech_api():
    """
    OpenAI API compatible endpoint for generating speech from text.
    It supports a limited set of parameters.
    """
    data = request.get_json()

    # Extract parameters from the request
    # OpenAI API compatible parameters only
    text = data.get("input")
    model = data.get("model", config.MODEL)
    voice = data.get("voice")
    response_format = data.get("response_format", "wav")

    print(f"Got request: {data}")

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

    # Generate audio from the text
    audio_data = tts.generate_audio(text, voice, model_name=model)

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
    """
    Endpoint for generating audio from text using the TTS model.
    This endpoint accepts more parameters used by Chatterbox.
    """
    data = request.get_json()

    # Extract parameters from the request
    text = data.get("text")
    voice = data.get("predefined_voice_id")
    model = data.get("model", config.MODEL)
    speed = float(data.get("speed_factor", 1.0))
    cfg = float(data.get("cfg_weight", config.AUDIO_CFG_WEIGHT))
    temperature = float(data.get("temperature", config.AUDIO_TEMPERATURE))
    exaggeration = float(data.get("exaggeration", config.AUDIO_EXAGGERATION))
    response_format = data.get("output_format", "wav")
    seed = data.get("seed", config.SEED)
    language_id = data.get("language_id", config.LANGUAGE_ID)

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

    if model not in config.SUPPORTED_MODELS:
        return jsonify({"error": "Unsupported model specified."}), 400

    if language_id not in config.SUPPORTED_LANGUAGE_IDS:
        return jsonify({"error": "Unsupported language id specified."}), 400

    # Generate audio from the text
    audio_data = tts.generate_audio(
        text,
        voice,
        speed,
        cfg,
        temperature,
        exaggeration,
        chunk_size,
        seed,
        model,
        language_id,
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


@app.route("/voices", methods=["GET"])
def get_voices_api():
    return jsonify({"voices": config.SUPPORTED_VOICES})


@app.route("/models", methods=["GET"])
def get_models_api():
    return jsonify({"models": config.SUPPORTED_MODELS})


@app.route("/languages", methods=["GET"])
def get_languages_api():
    return jsonify({"languages": config.SUPPORTED_LANGUAGE_IDS})


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


# These are strictly for ST to avoid errors
@app.get("/get_reference_files")
def get_reference_files_api():
    # do nothing
    return "[]"


@app.get("/api/ui/initial-data")
def get_api_ui_initial_data():
    # do nothing
    return "{}"
