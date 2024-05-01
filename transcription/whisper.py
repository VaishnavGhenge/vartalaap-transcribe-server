from typing import Dict, Optional, Union
import numpy as np
import torch
import whisper
from whisper import Whisper

class WhisperModel:
    def __init__(self, model_size="tiny", language="en", beam=5, task="transcribe") -> None:
        self.model_size: str = model_size
        self.language: str = language
        self.beam: int = beam
        self.task: str = task

        self.model: Whisper = whisper.load_model(self.model_size, language=self.language, beam=self.beam, task=self.task)

    def transcribe(
            self,
            audio_data: Union[str, np.ndarray, torch.Tensor], 
            no_speech_threshold: Optional[float] = 0.6
        ) -> str:
        """
            Transcribes audio using Whisper model.

            Parameters:
                audio: Union[str, np.ndarray, torch.Tensor]
                    The path to the audio file to open, or the audio waveform

                no_speech_threshold: float
                    If the no_speech probability is higher than this value AND the average log probability
                    over sampled tokens is below `logprob_threshold`, consider the segment as silent

            Returns:
                A str of transcribed text
        """

        result: Dict[str, any] = self.model.transcribe(audio_data, no_speech_threshold=no_speech_threshold)

        return result.get("text")
