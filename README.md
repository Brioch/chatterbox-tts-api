# Chatterbox-tts-api

Serve a [Chatterbox](https://huggingface.co/ResembleAI/chatterbox) TTS server with an [OpenAI Compatible API Speech endpoint](https://platform.openai.com/docs/api-reference/audio/createSpeech).

## Install

### Using uv

`uv` is supported as a faster alternative to conda and pip.

```sh
uv sync
uv run server.py
```

### Using pip

Chatterbox recommends Python 3.11. You can use `conda` to install it. If you're already running Python 3.11, you can just use a `venv` (`python -m venv venv && source venv/bin/activate`) and ignore the conda part.

```sh
conda create -n chatterbox python=3.11
conda activate chatterbox
pip install -r requirements.txt
```

### Using Podman or Docker

#### Build

A Dockerfile is provided to build an image for CUDA.

```sh
podman build -t chatterbox-tts-api .
podman run -it --rm -e 'API_HOST=0.0.0.0' -e 'API_PORT=5001' -e 'SUPPORTED_VOICES=alloy' -e 'VOICES_DIR=/app/voices' -v /path/to/voices:/app/voices -p 5001:5001 --device nvidia.com/gpu=all chatterbox-tts-server
```

#### Compose

A `compose.yaml` file is provided. It is configured for Docker, Podman and CUDA. Parameters can be set using a `.env` file.

```sh
cp .env.dist .env
podman compose up
```

## Usage

```sh
python server.py
```

Server will run by default on http://127.0.0.1:5001/v1/audio/speech.

Parameters are set with environment variables.

Copy `.env.dist` to `.env` and edit it to your needs.

```sh
cp .env.dist .env
```

Voice are expected to be wav audio files. For example, with a directory `/home/user/voices` containing `alloy.wav`, you would run the server with the following env vars:

- `SUPPORTED_VOICES=alloy`
- `VOICES_DIR=/home/user/voices`

### Environment Variables

```
API_HOST              Host to run the server on. Default: 0.0.0.0
API_PORT              Port to run the server on. Default: 5001
VOICES_DIR            Path to the audio prompt files dir.
SUPPORTED_VOICES      Comma-separated list of supported voices. Example: 'alloy,ash'. Default is empty so all voices in the voices dir are loaded.
EXAGGERATION          Exaggeration factor for the audio. Default: 0.5
TEMPERATURE           Temperature for the audio. Default: 0.8
CFG                   CFG weight for the audio. Default: 0.5
MODEL                 Model to use. Default: Chatterbox. Supported values: Chatterbox, Chatterbox-Multilingual, Chatterbox-Turbo
CORS_ALLOW_ORIGIN     CORS allowed origin. Default: *
SEED                  Seed for reproducibility. Default: 0 (random)
LANGUAGE_ID           Language ID for the multilingual model. Default: en (english). Supported values: ar, da, de, el, en, es, fi, fr, he, hi, it, ja, ko, ms, nl, no, pl, pt, ru, sv, sw, tr, zh
WEB_PORT              Port to run the web UI on when using the Dockerfile. Default: 8080
```

### Using the API

See [OpenAI Compatible API Speech endpoint](https://platform.openai.com/docs/api-reference/audio/createSpeech). This API takes a json containing an input text and a voice and replies with the TTS audio data. 

Example API call with `curl`:

```sh
curl -X POST http://localhost:5001/v1/audio/speech -H "Content-Type: application/json" -d '{"input": "Hello, this is a test.", "voice": "alloy"}' --output speech.wav
```

### Using the web UI

First, run the API server. Then start the web UI server:

```sh
python -m http.server 8080 -d public -b 127.0.0.1
```

Then open `http://localhost:8080` in your browser. You can set the API URL, enter text and select a voice to generate speech.

### Usage in SillyTavern

See [SillyTavern docs](docs/usage-sillytavern.md)
