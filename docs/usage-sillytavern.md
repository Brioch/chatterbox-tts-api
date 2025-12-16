# SillyTavern

## Chatterbox

SillyTavern is compatible with the `Chatterbox` TTS provider. Select it and set the base URL to your server's address (e.g. `http://127.0.0.1:5001`).

This option retrieves the voices from the server and allows for more advanced settings, such as `cfg_weight`, `temperature`, and `exaggeration`.

## OpenAI Compatible API

This program's OpenAI compatible API can alternatively be used as a SillyTavern TTS endpoint.

Select TTS Provider: `OpenAI Compatible`

Provider Endpoint: `http://127.0.0.1:5001/v1/audio/speech` (default value, change as needed)

Available Voices (comma separated): `voice1,voice2` (set voices from your server's `supported_voices`)

Model and API key settings are ignored.

![screenshot](../img/sillytavern.png)
