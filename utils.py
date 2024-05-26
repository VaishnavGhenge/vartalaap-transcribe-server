from typing import TypedDict, Union


LANGUAGE_CODES = (
    "af",
    "am",
    "ar",
    "as",
    "az",
    "ba",
    "be",
    "bg",
    "bn",
    "bo",
    "br",
    "bs",
    "ca",
    "cs",
    "cy",
    "da",
    "de",
    "el",
    "en",
    "es",
    "et",
    "eu",
    "fa",
    "fi",
    "fo",
    "fr",
    "gl",
    "gu",
    "ha",
    "haw",
    "he",
    "hi",
    "hr",
    "ht",
    "hu",
    "hy",
    "id",
    "is",
    "it",
    "ja",
    "jw",
    "ka",
    "kk",
    "km",
    "kn",
    "ko",
    "la",
    "lb",
    "ln",
    "lo",
    "lt",
    "lv",
    "mg",
    "mi",
    "mk",
    "ml",
    "mn",
    "mr",
    "ms",
    "mt",
    "my",
    "ne",
    "nl",
    "nn",
    "no",
    "oc",
    "pa",
    "pl",
    "ps",
    "pt",
    "ro",
    "ru",
    "sa",
    "sd",
    "si",
    "sk",
    "sl",
    "sn",
    "so",
    "sq",
    "sr",
    "su",
    "sv",
    "sw",
    "ta",
    "te",
    "tg",
    "th",
    "tk",
    "tl",
    "tr",
    "tt",
    "uk",
    "ur",
    "uz",
    "vi",
    "yi",
    "yo",
    "zh",
    "yue",
)

DEFAULT_MODEL = "faster-whisper"
DEFAULT_MODEL_SIZE = "tiny"
DEFAULT_TRANSCRIBE_LANGUAGE = "en"
DEFAULT_DEVICE = "cpu"
DEFAULT_COMPUTE_TYPE = "int8"


class TranscribeData(TypedDict):
    model: str
    model_size: str
    language: str
    device: str
    compute_type: str


def get_default_transcribe_config(validated_data) -> TranscribeData:
    default_data = {}

    if "model" not in validated_data:
        default_data["model"] = DEFAULT_MODEL

    if "model_size" not in validated_data:
        default_data["model_size"] = DEFAULT_MODEL_SIZE

    if "language" not in validated_data:
        default_data["language"] = DEFAULT_TRANSCRIBE_LANGUAGE

    if "device" not in validated_data:
        default_data["device"] = DEFAULT_DEVICE

    if "compute_type" not in validated_data:
        default_data["compute_type"] = DEFAULT_COMPUTE_TYPE

    print(f"\03[92m{default_data}\033[0m")

    return default_data