from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Category, Product, StockMovement
from app.schemas.product import (
    ProductCreateSchema,
    ProductListSchema,
    ProductQuerySchema,
    ProductSchema,
    ProductUpdateSchema,
)
from app.schemas.stock_movement import StockAdjustmentSchema, StockMovementSchema

blueprint = Blueprint("products", __name__, url_prefix="/api/v1/products", description="Products")


def get_product(product_id):
    return db.session.get(Product, product_id) or abort(404, message="Product not found.", code="not_found")


@blueprint.route("")
class ProductCollection(MethodView):
    @blueprint.arguments(ProductCreateSchema)
    @blueprint.response(201, ProductSchema)
    def post(self, data):
        if not db.session.get(Category, data["category_id"]):
            abort(404, message="Category not found.", code="not_found")
        product = Product(**data)
        db.session.add(product)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="A product with this SKU already exists.", code="duplicate_sku")
        return product

    @blueprint.arguments(ProductQuerySchema, location="query")
    @blueprint.response(200, ProductListSchema)
    def get(self, query_args):
        query = select(Product)
        search = query_args.get("search")
        if search:
            query = query.where(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
        if "category_id" in query_args:
            query = query.where(Product.category_id == query_args["category_id"])
        if "min_price" in query_args:
            query = query.where(Product.price >= query_args["min_price"])
        if "max_price" in query_args:
            query = query.where(Product.price <= query_args["max_price"])
        if query_args.get("low_stock"):
            query = query.where(Product.quantity <= Product.low_stock_threshold)

        sort = query_args["sort"]
        sort_column = {"name": Product.name, "price": Product.price, "quantity": Product.quantity}.get(sort.lstrip("-"))
        query = query.order_by(sort_column.desc() if sort.startswith("-") else sort_column.asc())

        pagination = db.paginate(
            query, page=query_args["page"], per_page=query_args["per_page"], error_out=False
        )
        return {
            "items": pagination.items,
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "pages": pagination.pages,
                "total": pagination.total,
            },
        }


@blueprint.route("/<int:product_id>")
class ProductResource(MethodView):
    @blueprint.response(200, ProductSchema)
    def get(self, product_id):
        return get_product(product_id)

    @blueprint.arguments(ProductUpdateSchema)
    @blueprint.response(200, ProductSchema)
    def patch(self, data, product_id):
        product = get_product(product_id)
        if "category_id" in data and not db.session.get(Category, data["category_id"]):
            abort(404, message="Category not found.", code="not_found")
        for key, value in data.items():
            setattr(product, key, value)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="A product with this SKU already exists.", code="duplicate_sku")
        return product

    @blueprint.response(204)
    def delete(self, product_id):
        product = get_product(product_id)
        db.session.delete(product)
        db.session.commit()
        return "", 204


@blueprint.route("/<int:product_id>/stock")
class ProductStock(MethodView):
    @blueprint.arguments(StockAdjustmentSchema)
    @blueprint.response(200, ProductSchema)
    def post(self, data, product_id):
        product = get_product(product_id)
        change = data["quantity_change"]
        if change == 0:
            abort(400, message="Stock adjustment cannot be zero.", code="invalid_stock_adjustment")
        if product.quantity + change < 0:
            abort(400, message="Stock cannot become negative.", code="insufficient_stock")
        product.quantity += change
        db.session.add(StockMovement(product=product, quantity_change=change, reason=data["reason"]))
        db.session.commit()
        return product


@blueprint.route("/<int:product_id>/movements")
class ProductMovements(MethodView):
    @blueprint.response(200, StockMovementSchema(many=True))
    def get(self, product_id):
        product = get_product(product_id)
        return db.session.scalars(
            select(StockMovement)
            .where(StockMovement.product_id == product.id)
            .order_by(StockMovement.created_at.desc(), StockMovement.id.desc())
        ).all()
