import time
import io
import librosa

from flask import Flask, request, jsonify
from flask_cors import CORS

from worker import make_celery
from transcribe import transcribe_with_whisper

app = Flask(__name__)

CORS(app)

app.config.update(
    CELERY_BROKER_URL='redis://:486590@localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://:486590@localhost:6379/0',
    TASK_IGNORE_RESULT=True,
)
celery_app = make_celery(app)


@celery_app.task
def transcribe_audio(resampled_data):
    try:
        # Transcription start time
        transcribe_start_time = time.time()

        transcription = transcribe_with_whisper(resampled_data)

        # Transcription end time
        transcribe_end_time = time.time()

        print("\033[92mTranscripted text:", transcription, "\033[0m")

        return transcription, transcribe_end_time - transcribe_start_time

    except Exception as e:
        print("\033[92mError:", e, "\033[0m")
        return str(e)

@app.route("/transcribe-bytes", methods=["POST"])
def transcribe_bytes():
    try:
        # Check if audio file is present in the request
        if 'audio_file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        audio_file = request.files.get('audio_file')

        # Check if audio_file is sent in files
        if not audio_file:
            return jsonify({"error": "`audio_file` is missing in request.files"}), 400

        # Check if the file is present
        if audio_file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        print(audio_file)

        bt = audio_file.read()

        memory_file = io.BytesIO(bt)

        data, sample_rate = librosa.load(memory_file)

        resample_data = librosa.resample(data, orig_sr=sample_rate, target_sr=16000)

        print("calling transcribe")

        # Send audio chunks to the Celery task for transcription
        task = transcribe_audio.delay(resample_data)

        return jsonify({
            "task_id": task.id,
            "status": "PENDING"
        })

    except Exception as e:
        print("\033[92mError:", e, "\033[0m")
        return jsonify({"error": str(e)})


@app.route("/check-task-status/<task_id>", methods=["GET"])
def check_task_status(task_id):
    # Check the status of the Celery task with the given task ID
    task = transcribe_audio.AsyncResult(task_id)
    
    # Return the task status in the response
    return jsonify({
        "task_id": task.id,
        "status": task.status
    })

@app.route("/get-transcription/<task_id>", methods=["GET"])
def get_transcription(task_id):
    # Check the status of the Celery task with the given task ID
    task = transcribe_audio.AsyncResult(task_id)
    
    # If task is successful, return the transcription
    if task.status == 'SUCCESS':
        return jsonify({
            "task_id": task.id,
            "status": task.status,
            "transcription": task.result
        })
    else:
        return jsonify({
            "task_id": task.id,
            "status": task.status
        })
