import torch
import whisper
import numpy as np
from typing import Dict, Optional, Union
from whisper import Whisper

from utils import TranscribeData


class WhisperModel:
    def __init__(self, config: TranscribeData, beam=5, task="transcribe") -> None:
        self.model_size: str = config["model_size"]
        self.language: str = config["language"]
        self.beam: int = beam
        self.task: str = task

        self.model: Whisper = whisper.load_model(
            self.model_size,
            language=self.language,
            beam=self.beam,
            task=self.task,
        )

    def get_transcribed_text(
            self,
            audio_data: Union[str, np.ndarray, torch.Tensor],
            no_speech_threshold: Optional[float] = 0.6
    ) -> str:
        """
            Transcribes audio using Whisper model.

            Parameters:
                audio_data: Union[str, np.ndarray, torch.Tensor]
                    The path to the audio file to open, or the audio waveform

                no_speech_threshold: float
                    If the no_speech probability is higher than this value AND the average log probability
                    over sampled tokens is below `logprob_threshold`, consider the segment as silent

            Returns:
                A str of transcribed text
        """

        result: Dict[str, any] = self.model.transcribe(audio_data, no_speech_threshold=no_speech_threshold)

        return result.get("text")
