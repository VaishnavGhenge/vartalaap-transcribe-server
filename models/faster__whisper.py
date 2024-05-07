from typing import Union, BinaryIO

import logging
import numpy as np
from faster_whisper import WhisperModel

from utils import TranscribeData


class FasterWhisper:
    def __init__(self, config: TranscribeData, beam_size=5, **kwargs):
        if config["language"] == "auto":
            self.language = None
        else:
            self.language = config["language"]

        self.beam_size = beam_size
        self.model = self.load_model(**config, **kwargs)

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

    def transcribe(self, audio: Union[str, BinaryIO, np.ndarray], init_prompt: str = "", **kwargs) -> str:
        segments, _ = self.model.transcribe(audio, language=self.language, initial_prompt=init_prompt, **kwargs)

        logging.warning(segments)

        return " ".join(segment.text for segment in segments)
