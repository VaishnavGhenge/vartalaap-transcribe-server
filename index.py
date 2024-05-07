import os
import json

from flask import Flask
from flask_cors import CORS
from flask import jsonify, request

from worker.config import make_celery
from worker.utils import transcribe

from marshmallow import Schema, fields, ValidationError, validate
from utils import (
    LANGUAGE_CODES, 
    DEFAULT_MODEL, 
    DEFAULT_MODEL_SIZE, 
    DEFAULT_TRANSCRIBE_LANGUAGE,
    DEFAULT_DEVICE,
    DEFAULT_COMPUTE_TYPE,
    get_default_transcribe_config,
    TranscribeData
)

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
def transcribe_audio(audio_bytes, config: TranscribeData):
    return transcribe(audio_bytes, config)


class TranscribeSchema(Schema):
    # TODO: explore how default works here
    model = fields.String(validate=validate.OneOf(["whisper", "faster-whisper"]), default=DEFAULT_MODEL)
    model_size = fields.String(validate=validate.OneOf(["tiny", "base", "small"]), default=DEFAULT_MODEL_SIZE)
    language = fields.String(validate=validate.OneOf(LANGUAGE_CODES), default=DEFAULT_TRANSCRIBE_LANGUAGE)
    device = fields.String(validate=validate.OneOf(["cpu", "cuda"]), default=DEFAULT_DEVICE)
    compute_type = fields.String(validate=validate.OneOf(["int8", "float16", "float32"]), default=DEFAULT_COMPUTE_TYPE)


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
    
    request_data = json.loads(request.form['config'])

    schema = TranscribeSchema()

    validated_data: TranscribeData = None
    try:
        loaded_data = schema.load(request_data)

        validated_data = get_default_transcribe_config(loaded_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages})
    
    if validated_data:
        audio_bytes = audio_file.read()

        # Send audio chunks to the Celery task for models
        task = transcribe_audio.delay(audio_bytes)

        return jsonify({
            "task": {
                "task_id": task.id,
                "status": task.status,
            },
            "model": validated_data.get("model"),
            "model_size": validated_data.get("model_size"),
            "language": validated_data.get("language"),
        })
    else:
        return jsonify({"error": "Invalid request data"}), 400


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
