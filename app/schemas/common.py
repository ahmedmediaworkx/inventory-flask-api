from marshmallow import Schema, fields


class ErrorSchema(Schema):
    code = fields.String(required=True)
    message = fields.String(required=True)
    details = fields.Dict(required=True)
