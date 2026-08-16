from marshmallow import Schema, fields, validate

positive_or_zero = validate.Range(min=0)


class ProductCreateSchema(Schema):
    sku = fields.String(required=True, validate=validate.Length(min=1, max=64))
    name = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True, load_default=None)
    price = fields.Decimal(required=True, as_string=True, validate=positive_or_zero)
    low_stock_threshold = fields.Integer(load_default=5, validate=positive_or_zero)
    category_id = fields.Integer(required=True, validate=positive_or_zero)


class ProductUpdateSchema(Schema):
    sku = fields.String(validate=validate.Length(min=1, max=64))
    name = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String(allow_none=True)
    price = fields.Decimal(as_string=True, validate=positive_or_zero)
    low_stock_threshold = fields.Integer(validate=positive_or_zero)
    category_id = fields.Integer(validate=positive_or_zero)


class ProductSchema(Schema):
    id = fields.Integer(dump_only=True)
    sku = fields.String(required=True)
    name = fields.String(required=True)
    description = fields.String(allow_none=True)
    price = fields.Decimal(as_string=True, required=True)
    quantity = fields.Integer(dump_only=True)
    low_stock_threshold = fields.Integer(required=True)
    category_id = fields.Integer(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ProductQuerySchema(Schema):
    search = fields.String()
    category_id = fields.Integer(validate=validate.Range(min=1))
    min_price = fields.Decimal(validate=positive_or_zero)
    max_price = fields.Decimal(validate=positive_or_zero)
    low_stock = fields.Boolean()
    sort = fields.String(
        load_default="name",
        validate=validate.OneOf(["name", "-name", "price", "-price", "quantity", "-quantity"]),
    )
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=20, validate=validate.Range(min=1, max=100))


class PaginationSchema(Schema):
    page = fields.Integer(required=True)
    per_page = fields.Integer(required=True)
    pages = fields.Integer(required=True)
    total = fields.Integer(required=True)


class ProductListSchema(Schema):
    items = fields.List(fields.Nested(ProductSchema), required=True)
    pagination = fields.Nested(PaginationSchema, required=True)
