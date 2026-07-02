from marshmallow import Schema, fields, validate, validates, ValidationError


class SetBudgetSchema(Schema):
    amount = fields.Float(
        required=True,
        validate=validate.Range(min=0, error="Budget amount must be positive"),
    )
    month = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=12, error="Month must be 1-12"),
    )
    year = fields.Integer(
        required=True,
        validate=validate.Range(min=2000, max=2100, error="Invalid year"),
    )
    category_id = fields.Integer(allow_none=True, load_default=None)


class BudgetResponseSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    category_id = fields.Integer(dump_only=True, allow_none=True)
    category_name = fields.String(dump_only=True, allow_none=True)
    category_icon = fields.String(dump_only=True, allow_none=True)
    category_color = fields.String(dump_only=True, allow_none=True)
    month = fields.Integer(dump_only=True)
    year = fields.Integer(dump_only=True)
    amount = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True, format="iso")
    updated_at = fields.DateTime(dump_only=True, format="iso")
