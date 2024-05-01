from typing import Optional, Union

import numpy as np
import torch
import whisper


def transcribe_with_whisper(resampled_data) -> str:
    """
        Transcribes audio using Whisper model.
        
        Args:
            resampled_data (Union[str, bytes]): Either path to the audio file or bytes representing the audio file.

        Returns:
            str: Transcribed text.
    """

    model = whisper.load_model("tiny")

    result = model.transcribe(resampled_data, task="transcribe", language="en", fp16=False)

    transcribed_text = result.get("text")

    return transcribed_text


class Whisper:
    def __init__(self, model_size="tiny", language="en", beam=5, task="transcribe") -> None:
        self.model_size: str = model_size
        self.language: str = language
        self.beam: int = beam
        self.task: str = task

        self.model: Whisper = whisper.load_model(self.model_size, language=self.language, beam=self.beam,
                                                 task=self.task)

    def transcribe(
            self,
            audio_data: Union[str, np.ndarray, torch.Tensor],
            no_speech_threshold: Optional[float] = 0.6
    ):
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

        result = self.model.transcribe(audio_data, no_speech_threshold=no_speech_threshold)

        return result.get("text")
