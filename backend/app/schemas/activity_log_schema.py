from marshmallow import Schema, fields, validate


class ActivityLogSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    action = fields.String(dump_only=True)
    entity_type = fields.String(dump_only=True)
    entity_id = fields.Integer(dump_only=True, allow_none=True)
    details = fields.String(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True, format="iso")
