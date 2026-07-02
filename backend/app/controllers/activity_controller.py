from datetime import datetime, timezone

from flask_jwt_extended import get_jwt_identity

from app import db
from app.models import ActivityLog
from app.models.user import User
from app.schemas.activity_log_schema import ActivityLogSchema
from app.utils.responses import success_response, error_response

activity_schema = ActivityLogSchema()
activity_list_schema = ActivityLogSchema(many=True)


def log_activity(user_id, action, entity_type, entity_id=None, details=None):
    log = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.session.add(log)
    db.session.commit()


def list_activities():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))
    if not user:
        return error_response("User not found", 404)

    activities = (
        ActivityLog.query
        .filter_by(user_id=user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(20)
        .all()
    )

    return success_response(
        data={"activities": activity_list_schema.dump(activities)},
        message="Activities retrieved",
    )
