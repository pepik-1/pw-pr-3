from flask import Flask, jsonify
from .provider.polza import PolzaProvider

from werkzeug.exceptions import RequestEntityTooLarge

def create_app(provider: PolzaProvider | None = None) -> Flask:
    app = Flask(__name__)
    
    from .routes import MAX_AUDIO_BYTES, REQUEST_OVERHEAD_BYTES, bp
    
    app.config.from_mapping(
        MAX_CONTENT_LENGTH=MAX_AUDIO_BYTES + REQUEST_OVERHEAD_BYTES,
        TRANSCRIPTION_PROVIDER=(provider if provider is not None else PolzaProvider())
    )
    
    app.register_blueprint(bp)
    
    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_upload():
        return jsonify(error="Аудиофайл должен быть не больше 10 МБ."), 413
    
    return app