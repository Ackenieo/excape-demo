import base64
import hashlib
import uuid

from flask import current_app

from app.extensions import db
from app.models.profile_image import ProfileImage
from app.api.upload_logic import is_allowed_avatar_url


DEFAULT_PROFILE_IMAGE_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
DEFAULT_PROFILE_IMAGE_STORAGE_KEY = "default-avatar-01"
DEFAULT_PROFILE_IMAGE_MIME_TYPE = "image/png"
DEFAULT_PROFILE_IMAGE_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4////fwAJ+wP9"
    "KobjigAAAABJRU5ErkJggg=="
)
MAX_PROFILE_IMAGE_BYTES = 256 * 1024
ALLOWED_PROFILE_IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}


def _sha256_hex(binary_data):
    return hashlib.sha256(binary_data).hexdigest()


def _decode_base64_payload(image_base64):
    if not image_base64 or not isinstance(image_base64, str):
        return None
    payload = image_base64.strip()
    if not payload:
        return None
    if "," in payload and payload.lower().startswith("data:"):
        payload = payload.split(",", 1)[1]
    try:
        return base64.b64decode(payload, validate=True)
    except Exception:
        return None


def build_default_profile_image_payload():
    binary_data = base64.b64decode(DEFAULT_PROFILE_IMAGE_BASE64)
    return {
        "id": DEFAULT_PROFILE_IMAGE_ID,
        "storage_key": DEFAULT_PROFILE_IMAGE_STORAGE_KEY,
        "storage_kind": "default",
        "binary_data": binary_data,
        "mime_type": DEFAULT_PROFILE_IMAGE_MIME_TYPE,
        "byte_size": len(binary_data),
        "checksum": _sha256_hex(binary_data),
    }


def ensure_default_profile_image():
    image = ProfileImage.query.filter_by(
        storage_key=DEFAULT_PROFILE_IMAGE_STORAGE_KEY
    ).first()
    if image:
        return image

    payload = build_default_profile_image_payload()
    image = ProfileImage(**payload)
    db.session.add(image)
    db.session.flush()
    return image


def get_default_profile_image():
    image = ProfileImage.query.filter_by(
        storage_key=DEFAULT_PROFILE_IMAGE_STORAGE_KEY
    ).first()
    if image:
        return image
    return ensure_default_profile_image()


def get_profile_image_by_id(image_id):
    return db.session.get(ProfileImage, image_id)


def resolve_player_profile_image(player):
    if getattr(player, "avatar_image", None) is not None:
        return player.avatar_image
    if getattr(player, "avatar_image_id", None):
        image = get_profile_image_by_id(player.avatar_image_id)
        if image:
            return image
    return get_default_profile_image()


def resolve_player_avatar_url(player, build_legacy_url):
    avatar_url = (getattr(player, "avatar_url", None) or "").strip()
    if avatar_url and is_allowed_avatar_url(avatar_url):
        return avatar_url

    default_avatar_url = current_app.config.get("DEFAULT_PROFILE_AVATAR_URL")
    if default_avatar_url:
        return default_avatar_url

    avatar_image = resolve_player_profile_image(player)
    return build_legacy_url(avatar_image.id if avatar_image else None)


def create_custom_profile_image(image_base64, mime_type):
    if mime_type not in ALLOWED_PROFILE_IMAGE_MIME_TYPES:
        return None

    binary_data = _decode_base64_payload(image_base64)
    if not binary_data:
        return None
    if len(binary_data) > MAX_PROFILE_IMAGE_BYTES:
        return None

    image = ProfileImage(
        storage_kind="custom",
        binary_data=binary_data,
        mime_type=mime_type,
        byte_size=len(binary_data),
        checksum=_sha256_hex(binary_data),
    )
    db.session.add(image)
    db.session.flush()
    return image


def assign_default_profile_image(default_image_id):
    image = get_profile_image_by_id(default_image_id)
    if not image or image.storage_kind != "default":
        return None
    return image
