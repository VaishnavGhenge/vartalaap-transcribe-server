import io
import time
from typing import Union

import librosa
import numpy as np
import torch

from models.openai_whisper import WhisperModel
from models.faster__whisper import FasterWhisper
from utils import TranscribeData


def get_resampled_audio(audio_bytes, target_sampling_rate: int = 16000) -> np.ndarray:
    memory_file = io.BytesIO(audio_bytes)

    data, sample_rate = librosa.load(memory_file)

    return librosa.resample(data, orig_sr=sample_rate, target_sr=target_sampling_rate)


def get_transcription_with_time(audio: np.ndarray, transcription_func, config: TranscribeData):
    start_time = time.time()
    transcript_text = transcription_func(audio, config)
    end_time = time.time()

    return {
        "transcription": transcript_text,
        "duration": end_time - start_time
    }


def transcribe(audio, config: TranscribeData):
    resampled_audio: np.ndarray = get_resampled_audio(audio)

    if config["model"] == "whisper":
        return get_transcription_with_time(resampled_audio, whisper_transcribe, config)

    return get_transcription_with_time(resampled_audio, faster_whisper_transcribe, config)


def whisper_transcribe(audio: Union[str, np.ndarray, torch.Tensor], config: TranscribeData) -> str:
    whisper = WhisperModel(model_size=config["model_size"], language=config["language"])

    return whisper.get_transcribed_text(audio)


def faster_whisper_transcribe(audio: Union[str, np.ndarray, torch.Tensor], config: TranscribeData) -> str:
    faster_whisper = FasterWhisper(model_size=config["model_size"], language=config["language"], device=config["device"], compute_type=config["compute_type"])

    return faster_whisper.get_transcribed_text(audio)
