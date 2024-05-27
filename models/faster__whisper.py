from typing import Union, BinaryIO

import logging
import time
import numpy as np
from functools import lru_cache
from faster_whisper import WhisperModel

from utils import TranscribeData


class FasterWhisper:
    def __init__(self, model_size=None, language=None, device=None, compute_type=None, beam_size=5, **kwargs):
        if language == "auto":
            self.language = None
        else:
            self.language = language

        self.beam_size = beam_size
        self.model = self.get_cached_model(model_size=model_size, device=device, compute_type=compute_type, **kwargs)

    lru_cache(maxsize=1)

    def get_cached_model(self, model_size=None, device=None, compute_type=None, **kwargs):
        return self.load_model(model_size=model_size, device=device, compute_type=compute_type, **kwargs)

    def load_model(self, model_size=None, device=None, compute_type=None, **kwargs):
        if model_size is None:
            raise ValueError("Model size must be provided")

        if device is None:
            raise ValueError("Device must be provided")

        if compute_type is None:
            raise ValueError("Compute type must be provided")

        # Using GPU prefered settings
        # return WhisperModel(model_size, device="cuda", compute_type="float16")

        return WhisperModel(model_size, device=device, compute_type=compute_type, **kwargs)

    def get_transcribed_text(self, audio: Union[str, BinaryIO, np.ndarray], init_prompt: str = "", **kwargs) -> str:
        print(f"\033[92mTranscribe using faster whisper model\033[0m")
        start_time = time.time()
        segments, _ = self.model.transcribe(audio, language=self.language, initial_prompt=init_prompt, **kwargs)
        print(f"\033[92mEnd Transcribing faster whisper model\033[0m Total time: ", time.time() - start_time)

        logging.warning(segments)

        return " ".join(segment.text for segment in segments)
