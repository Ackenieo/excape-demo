from flask import jsonify


PARAM_ERROR = 401
LEVEL_NOT_FOUND = 402
RUN_NOT_FOUND = 403
RUN_NOT_PLAYABLE = 404
CONTENT_INVALID = 405
CHALLENGE_INVALID = 406
USER_NOT_FOUND = 407
AVATAR_INVALID = 408
CUSTOM_NPC_INVALID = 409
NICKNAME_INVALID = 409
CUSTOM_NPC_CONTENT_INVALID = 410
SERVER_ERROR = 500


def success_response(data, status=200, message="ok"):
    return jsonify({"code": 0, "message": message, "data": data}), status


def error_response(code, message, status=400):
    return jsonify({"code": code, "message": message, "data": None}), status
