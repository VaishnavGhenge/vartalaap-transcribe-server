import os
import tempfile
from werkzeug.utils import secure_filename
import time
import uuid

from flask import Flask, request, jsonify
from flask_cors import CORS

from worker import make_celery
from transcribe import transcribe_with_whisper

app = Flask(__name__)

CORS(app)

app.config.update(
    CELERY_BROKER_URL='redis://root:panda@localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://root:panda@localhost:6379/0',
    TASK_IGNORE_RESULT=True,
)
celery_app = make_celery(app)

@app.route("/transcribe", methods=["POST"])
def transcribe():
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

    # Save the file with a unique name
    filename = secure_filename(audio_file.filename)
    unique_filename = os.path.join("uploads", str(uuid.uuid4()) + '_' + filename)
    # audio_file.save(unique_filename)
    
    # Read the contents of the audio file
    contents = audio_file.read()

    max_file_size = 500 * 1024 * 1024
    if len(contents) > max_file_size:
        return jsonify({"error": "File is too large"}), 400

    # Check if the file extension suggests it's a WAV file
    if not filename.lower().endswith('.wav'):
        # Delete the file if it's not a WAV file
        os.remove(unique_filename)
        return jsonify({"error": "Only WAV files are supported"}), 400

    print(f"\033[92m{filename}\033[0m")

    # Call Celery task asynchronously
    result = transcribe_audio.delay(contents)

    return jsonify({
        "task_id": result.id,
        "status": "pending"
    })


@celery_app.task
def transcribe_audio(contents):
    # Transcribe the audio
    try:
        # Create a temporary file to save the audio data
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_path = temp_audio.name
            temp_audio.write(contents)

            print(f"\033[92mFile temporary path: {temp_path}\033[0m")
            transcribe_start_time = time.time()

            # Transcribe the audio
            transcription = transcribe_with_whisper(temp_path)
            
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
