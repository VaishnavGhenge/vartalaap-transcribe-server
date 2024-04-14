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


@celery_app.task
def transcribe_audio(audio_chunks):
    try:
        transcribe_start_time = time.time()

        # Concatenate audio chunks into a single bytes object
        audio_data = b''.join(audio_chunks)

        # You would replace this function with your actual transcription logic
        # transcribe_with_whisper is just a placeholder here
        transcription = transcribe_with_whisper(audio_data)

        transcribe_end_time = time.time()

        print("\033[92mTranscripted text:", transcription, "\033[0m")

        return transcription, transcribe_end_time - transcribe_start_time

    except Exception as e:
        print("\033[92mError:", e, "\033[0m")
        return str(e)

@app.route("/transcribe-bytes", methods=["POST"])
def transcribe_bytes():
    try:
        # Read the audio chunks from the request
        audio_chunks = []
        while True:
            chunk = request.stream.read(1024)  # Adjust the chunk size as needed
            if not chunk:
                break
            audio_chunks.append(chunk)

        # Send audio chunks to the Celery task for transcription
        task = transcribe_audio.delay(audio_chunks)

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
