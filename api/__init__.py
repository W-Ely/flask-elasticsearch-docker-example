import datetime
import uuid

from flasgger import Swagger
from flask import Flask, g, jsonify, make_response, request
from werkzeug.exceptions import HTTPException

from api.errors import ApiException
from api.logger import clear_logging_context, LOGGER, set_logging_context

LOGGER.info("API BOOT: Initializing Flask")


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    Swagger(app)
    from api.endpoints import blueprint

    app.register_blueprint(blueprint)
    app.register_error_handler(HTTPException, handle_http_exception)
    app.register_error_handler(ApiException, handle_api_exception)
    app.register_error_handler(Exception, handle_default_exception)

    @app.before_request
    def log_request():
        clear_logging_context("method", "endpoint", "request_id", "session_id")
        g.request_start_time = datetime.datetime.now()
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        session_id = request.headers.get("X-Session-Id", None)
        context = {
            "method": request.method,
            "endpoint": request.path,
            "request_id": request_id,
            "session_id": session_id,
        }
        set_logging_context(**context)
        content_length = request.content_length if request.content_length is not None else 0
        LOGGER.info("Incoming Request", content_length=content_length)
        g.request_start_time = datetime.datetime.now()

    @app.after_request
    def log_response(response):
        elapsed_seconds = (datetime.datetime.now() - g.request_start_time).total_seconds()
        content_length = response.headers.get("Content-Length", 0)
        LOGGER.info(
            "Outgoing Response",
            status=response.status_code,
            content_length=content_length,
            elapsed_seconds=elapsed_seconds,
        )
        return response

    return app


def handle_api_exception(e):
    log = getattr(LOGGER, e.level)
    log("Error: {}".format(e.error), **e.extra)
    return make_response(jsonify({"message": {"error": e.error}}), e.status)


def handle_default_exception(e):
    LOGGER.error("Unexpected exception", exc_info=e)
    return make_response(jsonify({"message": {"error": "Internal Server Error"}}), 500)


def handle_http_exception(e):
    if e.code >= 500:
        LOGGER.error("HTTP exception", exc_info=e)
    return make_response(jsonify({"message": {"error": e.description}}), e.code)
