from flask import Blueprint
from app.models.level import Level
from app.api.responses import LEVEL_NOT_FOUND, error_response, success_response
from app.api.serializers import serialize_level_detail, serialize_level_item

level_bp = Blueprint("level", __name__, url_prefix="/api/v1/levels")


@level_bp.get("")
def get_levels():
    levels = Level.query.filter_by(status="active").all()
    return success_response({"items": [serialize_level_item(level) for level in levels]})


@level_bp.get("/<level_id>")
def get_level_detail(level_id):
    level = Level.query.get(level_id)
    if not level:
        return error_response(LEVEL_NOT_FOUND, "关卡不存在", status=404)

    return success_response(serialize_level_detail(level))
