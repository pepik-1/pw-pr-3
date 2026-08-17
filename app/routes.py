from pathlib import Path
from .provider.polza import PolzaError
from flask import Blueprint, current_app,jsonify,render_template,request

MAX_AUDIO_BYTES = 10 * 1024 * 1024
REQUEST_OVERHEAD_BYTES = 1024 * 1024
ALLOWED_EXTENSIONS = { 'm4a', 'mp3', 'wav', 'ogg', 'webm'}


bp = Blueprint('app', __name__)

@bp.before_request
def reject_cross_origin_uploads():
    if request.method != "POST":
        return None

    origin = request.headers.get('Origin')
    if origin and origin.strip('/') != request.host_url.rstrip('/'):
        return jsonify(error='Request from another site was declined'),403


@bp.get('/')
def index():
    return render_template("index.html")

@bp.post('/api/voice/upload')
def transcribe_audio():
    uploaded = request.files.get('audio')
    if uploaded is None or not uploaded.filename:
        return jsonify(error='set an audio'),400
    extention = Path(uploaded.filename).suffix.lower().lstrip('.')
    if extention not in ALLOWED_EXTENSIONS:
        return jsonify(error='Not supported format.')
    audio = uploaded.stream.read(MAX_AUDIO_BYTES+1)
    if not audio:
        return jsonify(error = 'Audio file is empty'),400

    if len(audio)>MAX_AUDIO_BYTES:
        return jsonify(error='audio file must be less then 10mb'),413
    provider = current_app.config['TRANSCRIPTION_PROVIDER']

    try:

        text = provider.transcribe(audio)

    except PolzaError as exc:

        return jsonify(error = 'provider configuration error'),502

    return jsonify(text=text)


