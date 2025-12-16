import io
import numpy as np
import wave
from pydub import AudioSegment
import utils
import config

_cached_tts_model = None
_current_model_name = None


def generate_audio(
    text: str,
    voice: str,
    speed: float = 1.0,
    cfg_weight: float = config.AUDIO_CFG_WEIGHT,
    temperature: float = config.AUDIO_TEMPERATURE,
    exaggeration: float = config.AUDIO_EXAGGERATION,
    chunk_size: int = 250,
    seed: int = 0,
    model_name: str = config.MODEL,
    language_id: str = config.LANGUAGE_ID,
):
    global _cached_tts_model, _current_model_name

    if _current_model_name != model_name:
        print(f"Loading model: {model_name}")
        if model_name == "Chatterbox-Turbo":
            from chatterbox.tts_turbo import ChatterboxTurboTTS as ChatterboxTTS
        elif model_name == "Chatterbox":
            from chatterbox.tts import ChatterboxTTS
        elif model_name == "Chatterbox-Multilingual":
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS as ChatterboxTTS
        else:
            raise ValueError(f"Unknown model: {model_name}")

        _cached_tts_model = ChatterboxTTS.from_pretrained(config.DEVICE)
        _current_model_name = model_name
    else:
        print(f"Using cached model: {model_name}")

    tts_model = _cached_tts_model

    if seed != 0:
        utils.set_seed(seed)  # For reproducibility

    voice_file = config.AUDIO_PROMPT_PATH + f"{voice}.wav"

    all_audio_data = []

    chunks = utils.chunk_text_by_sentences(text, chunk_size)

    # split in chunks
    for chunk in chunks:
        print(f"Generating audio for chunk: {chunk}")

        # Generate the waveform
        wav = tts_model.generate(
            chunk,
            audio_prompt_path=voice_file,
            exaggeration=exaggeration,
            temperature=temperature,
            cfg_weight=cfg_weight,
            **(
                {"language_id": language_id}
                if model_name == "Chatterbox-Multilingual"
                else {}
            ),
        )

        audio_data = wav.squeeze(0).numpy()
        audio_data = np.clip(audio_data, -1.0, 1.0)  # Clip to prevent saturation
        audio_data = (audio_data * 32767).astype(np.int16)
        all_audio_data.append(audio_data)

    audio_data = np.concatenate(all_audio_data)

    # Create a BytesIO object to write the WAV file
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 2 bytes for int16
        wf.setframerate(int(tts_model.sr * speed))  # Sample rate (adjust as needed)
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
