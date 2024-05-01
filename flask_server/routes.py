from flask import Blueprint, jsonify, request
from worker.tasks import transcribe_audio

transcribe_bp = Blueprint('transcribe', __name__)


@transcribe_bp.route("/transcribe-bytes", methods=["POST"])
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

    # Send audio chunks to the Celery task for transcription
    task = transcribe_audio.delay(audio_bytes)

    return jsonify({
        "task_id": task.id,
        "status": "PENDING"
    })


@transcribe_bp.route("/check-task-status/<task_id>", methods=["GET"])
def check_task_status(task_id):
    # Check the status of the Celery task with the given task ID
    task = transcribe_audio.AsyncResult(task_id)

    # Return the task status in the response
    return jsonify({
        "task_id": task.id,
        "status": task.status
    })


@transcribe_bp.route("/get-transcription/<task_id>", methods=["GET"])
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
