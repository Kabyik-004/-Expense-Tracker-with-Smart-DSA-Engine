from marshmallow import Schema, fields, validate


class ColumnMappingSchema(Schema):
    title = fields.String(allow_none=True, load_default=None)
    amount = fields.String(allow_none=True, load_default=None)
    date = fields.String(allow_none=True, load_default=None)
    description = fields.String(allow_none=True, load_default=None)
    category = fields.String(allow_none=True, load_default=None)
    type = fields.String(allow_none=True, load_default=None)
    balance = fields.String(allow_none=True, load_default=None)


class ImportPreviewResponseSchema(Schema):
    statement_id = fields.Integer(dump_only=True)
    filename = fields.String(dump_only=True)
    total_rows = fields.Integer(dump_only=True)
    valid_rows = fields.Integer(dump_only=True)
    sample_rows = fields.List(fields.Dict(), dump_only=True)
    detected_mapping = fields.Nested(ColumnMappingSchema, dump_only=True)
    column_preview = fields.Dict(dump_only=True)
    potential_duplicates = fields.Integer(dump_only=True)


class ImportConfirmSchema(Schema):
    statement_id = fields.Integer(required=True)
    mapping = fields.Nested(ColumnMappingSchema, required=True)
    skip_duplicates = fields.Boolean(load_default=True)
    default_category_id = fields.Integer(allow_none=True, load_default=None)


class ImportHistoryResponseSchema(Schema):
    id = fields.Integer(dump_only=True)
    filename = fields.String(dump_only=True)
    file_type = fields.String(dump_only=True)
    status = fields.String(dump_only=True)
    total_rows = fields.Integer(dump_only=True)
    imported_rows = fields.Integer(dump_only=True)
    skipped_rows = fields.Integer(dump_only=True)
    duplicate_rows = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True, format="iso")


class UploadResponseSchema(Schema):
    statement_id = fields.Integer(dump_only=True)
    filename = fields.String(dump_only=True)
    total_rows = fields.Integer(dump_only=True)
    detected_mapping = fields.Nested(ColumnMappingSchema, dump_only=True)
    column_preview = fields.Dict(dump_only=True)
    sample_rows = fields.List(fields.Dict(), dump_only=True)
