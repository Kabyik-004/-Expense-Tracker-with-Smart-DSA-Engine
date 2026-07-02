"""
Income schemas — validation and serialization for income records.
"""

from marshmallow import Schema, fields, validate


class CreateIncomeSchema(Schema):
    source = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100, error="Source must be 1-100 characters"),
    )
    amount = fields.Float(
        required=True,
        validate=validate.Range(min=0.01, error="Amount must be greater than zero"),
    )
    description = fields.String(
        validate=validate.Length(max=255, error="Description must be 255 characters or fewer"),
        load_default=None,
    )
    date = fields.Date(load_default=None)
    is_recurring = fields.Boolean(load_default=False)
    notes = fields.String(
        validate=validate.Length(max=2000, error="Notes must be 2000 characters or fewer"),
        load_default=None,
    )


class UpdateIncomeSchema(Schema):
    source = fields.String(
        validate=validate.Length(min=1, max=100, error="Source must be 1-100 characters"),
    )
    amount = fields.Float(
        validate=validate.Range(min=0.01, error="Amount must be greater than zero"),
    )
    description = fields.String(
        validate=validate.Length(max=255, error="Description must be 255 characters or fewer"),
    )
    date = fields.Date()
    is_recurring = fields.Boolean()
    notes = fields.String(
        validate=validate.Length(max=2000, error="Notes must be 2000 characters or fewer"),
    )


class IncomeResponseSchema(Schema):
    id = fields.Integer(dump_only=True)
    source = fields.String(dump_only=True)
    amount = fields.Float(dump_only=True)
    description = fields.String(dump_only=True)
    date = fields.Date(dump_only=True, format="iso")
    is_recurring = fields.Boolean(dump_only=True)
    notes = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True, format="iso")
    updated_at = fields.DateTime(dump_only=True, format="iso")
