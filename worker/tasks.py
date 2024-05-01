from index import celery_app
import io
import time
import librosa
from transcription.whisper import WhisperModel


@celery_app.task
def transcribe_audio(audio_bytes):
    memory_file = io.BytesIO(audio_bytes)

    data, sample_rate = librosa.load(memory_file)

    resample_data = librosa.resample(data, orig_sr=sample_rate, target_sr=32000)

    # Transcription start time
    transcribe_start_time = time.time()

    whisper = WhisperModel()

    transcription = whisper.transcribe(resample_data)

    # Transcription end time
    transcribe_end_time = time.time()

    return {
        "text": transcription,
        "processed_in": transcribe_end_time - transcribe_start_time
    }
