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

## Usage

```sh
python server.py path_to_voices_dir voices_list
```

Server will run by default on http://127.0.0.1:5001/v1/audio/speech.

Voice are expected to be wav audio files. For example, with a directory `/home/user/voices` containing `alloy.wav`, you would run `python server.py /home/user/voices alloy`

Running `server.py -h` will display the following help message.

```
usage: server.py [-h] [--port PORT] [--host HOST] [--exaggeration EXAGGERATION] [--temperature TEMPERATURE] [--cfg CFG]
                 [--model Chatterbox|Chatterbox-Turbo|Chatterbox-Multilingual] [--cors-allow-origin CORS_ALLOW_ORIGIN] [--seed SEED]
                 [--language-id ar|da|de|el|en|es|fi|fr|he|hi|it|ja|ko|ms|nl|no|pl|pt|ru|sv|sw|tr|zh]
                 voices_dir supported_voices

positional arguments:
  voices_dir            Path to the audio prompt files dir.
  supported_voices      Comma-separated list of supported voices. Example: 'alloy,ash,ballad,coral,echo,fable,onyx,nova,sage,shimmer,verse'

options:
  -h, --help            show this help message and exit
  --port PORT           Port to run the server on. Default: 5001
  --host HOST           Host to run the server on. Default: 127.0.0.1
  --exaggeration EXAGGERATION
                        Exaggeration factor for the audio. Default: 0.5
  --temperature TEMPERATURE
                        Temperature for the audio. Default: 0.8
  --cfg CFG             CFG weight for the audio. Default: 0.5
  --model Chatterbox|Chatterbox-Turbo|Chatterbox-Multilingual
                        Model to use. Default: Chatterbox
  --cors-allow-origin CORS_ALLOW_ORIGIN
                        CORS allowed origin. Default: http://localhost:8000
  --seed SEED           Seed for reproducibility. Default: 0 (random)
  --language-id ar|da|de|el|en|es|fi|fr|he|hi|it|ja|ko|ms|nl|no|pl|pt|ru|sv|sw|tr|zh
                        Language ID for the multilingual model. Default: en (english)
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
python -m http.server -d public -b 127.0.0.1
```

Then open `http://localhost:8000` in your browser. You can set the API URL, enter text and select a voice to generate speech.

### Podman / Docker

#### Build

A Dockerfile is provided to build an image for CUDA.

podman build -t chatterbox-tts-api .
podman run -it --rm -e 'API_HOST=0.0.0.0' -e 'API_PORT=5001' -e 'SUPPORTED_VOICES=alloy' -e 'VOICES_DIR=/app/voices' -v /path/to/voices:/app/voices -p 5001:5001 --device nvidia.com/gpu=all chatterbox-tts-server

#### Compose

A `compose.yaml` file is provided. It is configured for Podman and CUDA. Parameters can be set using a `.env` file.

```sh
cp .env.dist .env
podman compose up
```

### Usage in SillyTavern

See [SillyTavern docs](docs/usage-sillytavern.md)
