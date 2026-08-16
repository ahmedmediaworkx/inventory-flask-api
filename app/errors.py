from flask import jsonify
from werkzeug.exceptions import HTTPException


def error_payload(code, message, details=None):
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        data = getattr(error, "data", {})
        details = data.get("messages") or {}
        code = data.get("code") or error.name.lower().replace(" ", "_")
        message = data.get("message") or error.description
        return jsonify(error_payload(code, message, details)), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled exception", exc_info=error)
        return jsonify(error_payload("internal_server_error", "An unexpected error occurred.")), 500
