from marshmallow import Schema, fields, validate


class StockAdjustmentSchema(Schema):
    quantity_change = fields.Integer(required=True, validate=validate.Range(min=-2147483648, max=2147483647))
    reason = fields.String(required=True, validate=validate.Length(min=1, max=255))


class StockMovementSchema(Schema):
    id = fields.Integer(dump_only=True)
    product_id = fields.Integer(required=True)
    quantity_change = fields.Integer(required=True)
    reason = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)
