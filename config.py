import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

AUDIO_PROMPT_PATH = os.getenv("VOICES_DIR")

# check if path exists
if not os.path.exists(AUDIO_PROMPT_PATH):
    raise ValueError(f"Path {AUDIO_PROMPT_PATH} does not exist")

if AUDIO_PROMPT_PATH[-1] != "/":
    AUDIO_PROMPT_PATH += "/"

DEVICE = "cuda" if "CUDA_VERSION" in os.environ else "cpu"
API_PORT = os.getenv("API_PORT", "5001")
API_HOST = os.getenv("API_HOST", "0.0.0.0")
AUDIO_EXAGGERATION = float(os.getenv("AUDIO_EXAGGERATION", 0.5))
AUDIO_TEMPERATURE = float(os.getenv("AUDIO_TEMPERATURE", 0.8))
AUDIO_CFG_WEIGHT = float(os.getenv("AUDIO_CFG_WEIGHT", 0.5))
SUPPORTED_VOICES = os.getenv("SUPPORTED_VOICES", "").split(",")
SUPPORTED_RESPONSE_FORMATS = ["mp3", "opus", "aac", "flac", "wav", "pcm"]
MODEL = os.getenv("MODEL", "Chatterbox")
CORS_ALLOWED_ORIGIN = os.getenv("CORS_ALLOWED_ORIGIN", "*")
SEED = int(os.getenv("SEED", 0))
LANGUAGE_ID = os.getenv("LANGUAGE_ID", "en")

# if SUPPORTED_VOICES is empty, then we will use all voices in the AUDIO_PROMPT_PATH directory
if SUPPORTED_VOICES == [""]:
    print("No voices specified, using all voices in the AUDIO_PROMPT_PATH directory")

    SUPPORTED_VOICES = [
        f[:-4] for f in os.listdir(AUDIO_PROMPT_PATH) if f.endswith(".wav")
    ]

    print(f"Found {len(SUPPORTED_VOICES)} voices in the AUDIO_PROMPT_PATH directory")

print(f"🚀 Running on device: {DEVICE}")

if SEED != 0:
    import utils

    utils.set_seed(SEED)  # For reproducibility
