import whisper

def transcribe_with_whisper(audio_file: str) -> str:
    """
        Transcribes audio using Whisper model.
        
        Args:
            audio_chunk_bytes (Union[str, bytes]): Either path to the audio file or bytes representing the audio file.

        Returns:
            str: Transcribed text.
    """
    
    model = whisper.load_model("tiny")
    result = model.transcribe(audio_file, task="transcribe")

    transcribed_text = result.get("text")

    return transcribed_text or ""