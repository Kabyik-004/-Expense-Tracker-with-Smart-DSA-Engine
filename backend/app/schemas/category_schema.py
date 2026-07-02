from marshmallow import Schema, fields, validate

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    icon = fields.Str(allow_none=True)
    color = fields.Str(allow_none=True)
    budget_limit = fields.Float(allow_none=True)
    is_default = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)