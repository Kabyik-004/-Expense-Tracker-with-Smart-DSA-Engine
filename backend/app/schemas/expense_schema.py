"""
Expense schema — serialization / validation for expense payloads.
"""

from marshmallow import Schema, fields, validate


class CreateExpenseSchema(Schema):
    title = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100, error="Title must be 1-100 characters"),
    )
    amount = fields.Float(
        required=True,
        validate=validate.Range(min=0.01, error="Amount must be greater than zero"),
    )
    description = fields.String(
        validate=validate.Length(max=500, error="Description must be 500 characters or fewer"),
        load_default=None,
    )
    date = fields.Date(load_default=None)
    category_id = fields.Integer(load_default=None)
    payment_method = fields.String(
        validate=validate.OneOf(
            ["cash", "card", "upi", "bank_transfer"],
            error="Payment method must be cash, card, upi, or bank_transfer",
        ),
        load_default="cash",
    )
    is_recurring = fields.Boolean(load_default=False)
    notes = fields.String(
        validate=validate.Length(max=2000, error="Notes must be 2000 characters or fewer"),
        load_default=None,
    )


class UpdateExpenseSchema(Schema):
    title = fields.String(
        validate=validate.Length(min=1, max=100, error="Title must be 1-100 characters"),
    )
    amount = fields.Float(
        validate=validate.Range(min=0.01, error="Amount must be greater than zero"),
    )
    description = fields.String(
        validate=validate.Length(max=500, error="Description must be 500 characters or fewer"),
    )
    date = fields.Date()
    category_id = fields.Integer()
    payment_method = fields.String(
        validate=validate.OneOf(
            ["cash", "card", "upi", "bank_transfer"],
            error="Payment method must be cash, card, upi, or bank_transfer",
        ),
    )
    is_recurring = fields.Boolean()
    notes = fields.String(
        validate=validate.Length(max=2000, error="Notes must be 2000 characters or fewer"),
    )


class ExpenseResponseSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(dump_only=True)
    amount = fields.Float(dump_only=True)
    description = fields.String(dump_only=True)
    date = fields.Date(dump_only=True, format="iso")
    category_id = fields.Integer(dump_only=True)
    category_name = fields.String(dump_only=True)
    payment_method = fields.String(dump_only=True)
    is_recurring = fields.Boolean(dump_only=True)
    notes = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True, format="iso")
    updated_at = fields.DateTime(dump_only=True, format="iso")
