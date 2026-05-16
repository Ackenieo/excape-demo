from flask import jsonify

from app.api import api_bp


@api_bp.get("/health")
def health_check():
    return (
        jsonify(
            {
                "status": "ok",
                "service": "excape-api",
                "message": "Flask API is running",
            }
        ),
        200,
    )

@api_bp.get("/get_miao")
def get_miao():
    return jsonify({"message": "miao"}), 200

@api_bp.get("/ping")
def ping():
    return jsonify({"message": "pong"}), 200
