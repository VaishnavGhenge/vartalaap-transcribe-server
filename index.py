import os

from flask import Flask
from flask_cors import CORS
from flask import jsonify, request

from worker.config import make_celery
from worker.utils import transcribe

app = Flask(__name__)

CORS(app)

redis_url = "redis://:@localhost:6379/0"
if os.environ.get("PRODUCTION") == "true":
    redis_url = (f"redis://:"
                 f"{os.environ.get('REDIS_PASSWORD')}@{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/0")

app.config.update(
    CELERY_BROKER_URL=redis_url,
    CELERY_RESULT_BACKEND=redis_url,
)

celery_app = make_celery(app)


@celery_app.task
def transcribe_audio(audio_bytes):
    return transcribe(audio_bytes)


@app.route("/transcribe-bytes", methods=["POST"])
def transcribe_bytes():
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

    audio_bytes = audio_file.read()

    # Send audio chunks to the Celery task for models
    task = transcribe_audio.delay(audio_bytes)

    return jsonify({
        "task_id": task.id,
        "status": task.status
    })


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

    # If task is successful, return the models
    if task.status == 'SUCCESS':
        return jsonify({
            "task_id": task.id,
            "status": task.status,
            "models": task.result
        })
    else:
        return jsonify({
            "task_id": task.id,
            "status": task.status
        })


if __name__ == "__main__":
    app.run(debug=True)
