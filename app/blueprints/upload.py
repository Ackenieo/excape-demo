from flask import Blueprint, Response, current_app, request, send_file

from app.api.game_logic import utc_now
from app.api.responses import AVATAR_INVALID, PARAM_ERROR, success_response, error_response
from app.api.upload_logic import (
    get_avatar_upload_path,
    store_avatar_upload,
    validate_avatar_upload,
)


upload_bp = Blueprint("upload", __name__, url_prefix="/api/v1/uploads")


@upload_bp.post("/avatar")
def upload_avatar():
    device_id = (request.form.get("deviceId") or "").strip()
    biz_type = (request.form.get("bizType") or "").strip()
    file_storage = request.files.get("file")

    if not device_id or not biz_type:
        return error_response(PARAM_ERROR, "缺少 deviceId 或 bizType")

    is_valid, validation_result = validate_avatar_upload(file_storage, biz_type)
    if not is_valid:
        return error_response(AVATAR_INVALID, validation_result, status=400)

    stored = store_avatar_upload(file_storage)
    if stored is None:
        return error_response(AVATAR_INVALID, "头像上传失败", status=400)

    return success_response(
        {
            "url": stored["url"],
            "fileId": stored["fileId"],
            "uploadedAt": utc_now().isoformat().replace("+00:00", "Z"),
        },
        status=201,
    )


@upload_bp.get("/avatar/<path:file_id>")
def get_avatar_upload(file_id):
    file_path = get_avatar_upload_path(file_id)
    if file_path is None:
        return error_response(AVATAR_INVALID, "头像文件不存在", status=404)

    response: Response = send_file(file_path)
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response
