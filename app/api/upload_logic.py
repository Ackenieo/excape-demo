import os
import secrets
from pathlib import Path
from urllib.parse import urlparse

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


ALLOWED_IMAGE_SIGNATURES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],
}


def _normalize_filename(filename):
    return secure_filename(filename or "")


def _guess_extension(filename, mimetype):
    suffix = Path(filename).suffix.lower()
    if suffix in current_app.config["AVATAR_UPLOAD_ALLOWED_EXTENSIONS"]:
        return suffix
    fallback = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    return fallback.get(mimetype)


def _build_public_url(file_id):
    base_url = current_app.config["AVATAR_UPLOAD_PUBLIC_BASE_URL"]
    return f"{base_url}/avatar/{file_id}"


def _read_file_bytes(file_storage):
    file_storage.stream.seek(0)
    binary = file_storage.stream.read()
    file_storage.stream.seek(0)
    return binary


def _has_valid_signature(mimetype, binary_data):
    signatures = ALLOWED_IMAGE_SIGNATURES.get(mimetype, [])
    if mimetype == "image/webp":
        return binary_data.startswith(b"RIFF") and binary_data[8:12] == b"WEBP"
    return any(binary_data.startswith(signature) for signature in signatures)


def validate_avatar_upload(file_storage: FileStorage, biz_type: str):
    if not isinstance(file_storage, FileStorage) or not file_storage.filename:
        return False, "缺少头像文件"

    if biz_type != current_app.config["AVATAR_UPLOAD_BIZ_TYPE"]:
        return False, "bizType 非法"

    filename = _normalize_filename(file_storage.filename)
    if not filename:
        return False, "头像文件名非法"

    mimetype = (file_storage.mimetype or "").lower().strip()
    if mimetype not in current_app.config["AVATAR_UPLOAD_ALLOWED_MIME_TYPES"]:
        return False, "头像文件类型不受支持"

    extension = _guess_extension(filename, mimetype)
    if extension not in current_app.config["AVATAR_UPLOAD_ALLOWED_EXTENSIONS"]:
        return False, "头像文件扩展名不受支持"

    binary_data = _read_file_bytes(file_storage)
    if not binary_data:
        return False, "头像文件为空"

    size = len(binary_data)
    if size < current_app.config["AVATAR_UPLOAD_MIN_BYTES"]:
        return False, "头像文件过小"
    if size > current_app.config["AVATAR_UPLOAD_MAX_BYTES"]:
        return False, "头像文件过大"

    if not _has_valid_signature(mimetype, binary_data):
        return False, "头像文件内容与类型不匹配"

    return True, {
        "filename": filename,
        "extension": extension,
        "mimetype": mimetype,
        "binary_data": binary_data,
        "byte_size": size,
    }


def store_avatar_upload(file_storage: FileStorage):
    is_valid, result = validate_avatar_upload(
        file_storage,
        current_app.config["AVATAR_UPLOAD_BIZ_TYPE"],
    )
    if not is_valid:
        return None

    upload_dir = Path(current_app.config["AVATAR_UPLOAD_DIR"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_id = f"avatar_{secrets.token_hex(12)}{result['extension']}"
    destination = upload_dir / file_id
    with destination.open("wb") as handle:
        handle.write(result["binary_data"])

    return {
        "fileId": file_id,
        "url": _build_public_url(file_id),
        "storedPath": str(destination),
        "mimeType": result["mimetype"],
        "byteSize": result["byte_size"],
    }


def is_allowed_avatar_url(avatar_url: str):
    if not avatar_url or not isinstance(avatar_url, str):
        return False
    parsed = urlparse(avatar_url.strip())
    if parsed.scheme != "https" or not parsed.netloc:
        return False
    allowed_hosts = set(current_app.config["AVATAR_UPLOAD_ALLOWED_HOSTS"])
    return parsed.netloc.lower() in allowed_hosts


def get_avatar_upload_path(file_id: str):
    if not file_id or "/" in file_id or "\\" in file_id:
        return None
    filename = os.path.basename(file_id)
    path = Path(current_app.config["AVATAR_UPLOAD_DIR"]) / filename
    if not path.exists() or not path.is_file():
        return None
    return path
