import os

from flask import Flask
from flask_cors import CORS

from worker.config import make_celery
from flask_server.routes import transcribe_bp

app = Flask(__name__)

CORS(app)

app.register_blueprint(transcribe_bp, url_prefix="/transcribe")

redis_url = f"redis://:{os.environ.get('REDIS_PASSWD')}@{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/0"
app.config.update(
    CELERY_BROKER_URL=redis_url,
    CELERY_RESULT_BACKEND=redis_url,
)

celery_app = make_celery(app)

if __name__ == "__main__":
    app.run(debug=True)
