from typing import Union, BinaryIO

import logging
import numpy as np
from faster_whisper import WhisperModel


class FasterWhisper:
    def __init__(self, language="auto", model_size="base", beam_size=5, **kwargs):
        if language == "auto":
            self.language = None
        else:
            self.language = language

        self.beam_size = beam_size
        self.model = self.load_model(model_size, **kwargs)

    def load_model(self, model_size: str, device="cpu", compute_type="int8", **kwargs):
        if model_size is None:
            raise ValueError("Model size must be provided")

        # Using GPU
        # return WhisperModel(model_size, device="cuda", compute_type="float16")

        return WhisperModel(model_size, device=device, compute_type=compute_type, **kwargs)

    def transcribe(self, audio: Union[str, BinaryIO, np.ndarray], init_prompt: str = "", **kwargs) -> str:
        segments, info = self.model.transcribe(audio, language=self.language, initial_prompt=init_prompt, **kwargs)

        logging.warning(segments)

        return " ".join(segment.text for segment in segments)
