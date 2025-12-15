from flask import Flask, request, jsonify, send_file
import io
import numpy as np
import wave
import torch
import argparse
from pydub import AudioSegment

parser = argparse.ArgumentParser("server.py")
parser.add_argument("voices_dir", help="Path to the audio prompt files dir.", type=str)
parser.add_argument(
    "supported_voices",
    help="Comma-separated list of supported voices. Example: 'alloy,ash,ballad,coral,echo,fable,onyx,nova,sage,shimmer,verse'",
    type=str
)
parser.add_argument(
    "--port", help="Port to run the server on. Default: 5001", type=int, default=5001
)
parser.add_argument(
    "--host",
    help="Host to run the server on. Default: 127.0.0.1",
    type=str,
    default="127.0.0.1",
)
parser.add_argument(
    "--exaggeration",
    help="Exaggeration factor for the audio. Default: 0.5",
    type=float,
    default=0.5,
)
parser.add_argument(
    "--temperature",
    help="Temperature for the audio. Default: 0.8",
    type=float,
    default=0.8,
)
parser.add_argument(
    "--cfg",
    help="CFG weight for the audio. Default: 0.5",
    type=float,
    default=0.5,
)
parser.add_argument(
    "--model",
    help="Model to use. Default: Chatterbox",
    choices=["Chatterbox", "Chatterbox-Turbo"],
    metavar="Chatterbox|Chatterbox-Turbo",
    type=str,
    default="Chatterbox",
)  # Chatterbox-Turbo is not supported yet, as it requires a different API call and paramete
args = parser.parse_args()

AUDIO_PROMPT_PATH = args.voices_dir
if AUDIO_PROMPT_PATH[-1] != "/":
    AUDIO_PROMPT_PATH += "/"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
API_PORT = args.port
API_HOST = args.host
AUDIO_EXAGGERATION = args.exaggeration
AUDIO_TEMPERATURE = args.temperature
AUDIO_CFG_WEIGHT = args.cfg
SUPPORTED_VOICES=args.supported_voices.split(",")
SUPPORTED_RESPONSE_FORMATS = ["mp3", "opus", "aac", "flac", "wav", "pcm"]
MODEL="Chatterbox"

print(f"🚀 Running on device: {DEVICE}")

app = Flask(__name__)

if MODEL == "Chatterbox-Turbo":
    from chatterbox.tts_turbo import ChatterboxTurboTTS as ChatterboxTTS
elif MODEL=="Chatterbox":
    from chatterbox.tts import ChatterboxTTS

# Initialize the TTS model
tts_model = ChatterboxTTS.from_pretrained(DEVICE)

def generate_audio(text, voice, speed=1.0):
    voice_file = AUDIO_PROMPT_PATH + f"{voice}.wav"

    # Generate the waveform
    wav = tts_model.generate(
        text,
        audio_prompt_path=voice_file,
        exaggeration=AUDIO_EXAGGERATION,
        temperature=AUDIO_TEMPERATURE,
        cfg_weight=AUDIO_CFG_WEIGHT,
    )

    audio_data = wav.squeeze(0).numpy()
    audio_data = np.clip(audio_data, -1.0, 1.0)  # Clip to prevent saturation
    audio_data = (audio_data * 32767).astype(np.int16)

    # Create a BytesIO object to write the WAV file
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 2 bytes for int16
        wf.setframerate(tts_model.sr * speed)  # Sample rate (adjust as needed)
        wf.writeframes(audio_data.tobytes())

    wav_io.seek(0)
    return wav_io.getvalue()  # Return the bytes of the WAV file


def convert_audio_format(audio_data, response_format):
    if response_format == "wav":
        return audio_data

    # Convert the audio data to the desired format using pydub
    audio_segment = AudioSegment.from_wav(io.BytesIO(audio_data))

    # Convert to the desired format
    output_io = io.BytesIO()
    if response_format == "mp3":
        audio_segment.export(output_io, format="mp3")
    elif response_format == "flac":
        audio_segment.export(output_io, format="flac")
    elif response_format == "opus":
        audio_segment.export(output_io, format="opus")
    elif response_format == "aac":
        audio_segment.export(output_io, format="aac")
    elif response_format == "pcm":
        audio_segment.export(output_io, format="raw")  # PCM is raw audio

    output_io.seek(0)
    return output_io.getvalue()


@app.route("/v1/audio/speech", methods=["POST"])
def speech():
    data = request.get_json()

    # Extract parameters from the request
    text = data.get("input")
    voice = data.get("voice")
    speed = data.get("speed", 1.0)  # Default speed is 1.0
    response_format = data.get(
        "response_format", "wav"
    )  # Default response format is wav

    # Validate parameters
    if not text or len(text) > 4096:
        return (
            jsonify(
                {
                    "error": "Input text is required and must be less than 4096 characters."
                }
            ),
            400,
        )
    if voice not in SUPPORTED_VOICES:
        return jsonify({"error": "Unsupported voice specified."}), 400
    if response_format not in SUPPORTED_RESPONSE_FORMATS:
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
    audio_data = generate_audio(text, voice, speed)

    # Convert the audio data to the desired format
    converted_audio_data = convert_audio_format(audio_data, response_format)

    # Create a BytesIO object for the response
    audio_io = io.BytesIO(audio_data)
    audio_io.seek(0)

    # Set the appropriate MIME type based on the requested response format
    mime_type = "audio/" + response_format

    return send_file(
        audio_io,
        mimetype=mime_type,
        as_attachment=True,
        download_name=f"speech.{response_format}",
    )


if __name__ == "__main__":
    app.run(host=API_HOST, port=API_PORT)
