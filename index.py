import os
import tempfile
from werkzeug.utils import secure_filename
import time
import uuid
import io

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


@app.route("/transcribe-bytes", methods=["POST"])
def transcribe_bytes():
    # Read the audio file from request data
    audio_data = request.data

    # Transcribe the audio
    try:
        # Create a BytesIO object to work with bytes data
        audio = io.BytesIO(audio_data)

        print(f"\033[92mBytesIO object: {audio}\033[0m")

        task = transcribe_audio.delay(audio)

        return jsonify({
            "task_id": task.id,
            "status": "pending"
        })

    except Exception as e:
        print(f"\033[92mError: {e}\033[0m")
        return jsonify({"error": str(e)})


@celery_app.task
def transcribe_audio(contents):
    # Transcribe the audio
    try:
        print(f"\033[92mBytesIO object: {audio}\033[0m")
        transcribe_start_time = time.time()

        # Transcribe the audio
        transcription = transcribe_with_whisper(contents)

        transcribe_end_time = time.time()

        print(f"\033[92mTranscripted text: {transcription}\033[0m")

        return transcription, transcribe_end_time - transcribe_start_time

    except Exception as e:
        print(f"\033[92mError: {e}\033[0m")
        return str(e)
    
    # finally:
    #     # Cleanup temporary file
    #     if os.path.exists(temp_path):
    #         os.remove(temp_path)


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
