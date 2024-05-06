import io
import time
from typing import Union

import librosa
import numpy as np
import torch


def get_resampled_audio(audio_bytes, target_sampling_rate: int = 16000) -> np.ndarray:
    memory_file = io.BytesIO(audio_bytes)

    data, sample_rate = librosa.load(memory_file)

    return librosa.resample(data, orig_sr=sample_rate, target_sr=target_sampling_rate)


def get_transcription_with_time(audio: np.ndarray, transcription_func):
    start_time = time.time()
    transcript_text = transcription_func(audio)
    end_time = time.time()

    return {
        "transcription": transcript_text,
        "duration": end_time - start_time
    }


def transcribe(audio, model: str = "faster-whisper"):
    resampled_audio: np.ndarray = get_resampled_audio(audio)

    if model == "whisper":
        return get_transcription_with_time(resampled_audio, whisper_transcribe)

    return get_transcription_with_time(resampled_audio, faster_whisper_transcribe)


def whisper_transcribe(audio: Union[str, np.ndarray, torch.Tensor]) -> str:
    from models.openai_whisper import WhisperModel

    whisper = WhisperModel()

    return whisper.get_transcribed_text(audio)


def faster_whisper_transcribe(audio: Union[str, np.ndarray, torch.Tensor]) -> str:
    from models.faster__whisper import FasterWhisper
    
    faster_whisper = FasterWhisper()

    return faster_whisper.transcribe(audio)
