from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Category
from app.schemas.category import CategoryCreateSchema, CategorySchema, CategoryUpdateSchema

blueprint = Blueprint("categories", __name__, url_prefix="/api/v1/categories", description="Categories")


@blueprint.route("")
class CategoryCollection(MethodView):
    @blueprint.arguments(CategoryCreateSchema)
    @blueprint.response(201, CategorySchema)
    def post(self, data):
        category = Category(**data)
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="A category with this name already exists.", code="duplicate_category")
        return category

    @blueprint.response(200, CategorySchema(many=True))
    def get(self):
        return Category.query.order_by(Category.name).all()


@blueprint.route("/<int:category_id>")
class CategoryResource(MethodView):
    @blueprint.response(200, CategorySchema)
    def get(self, category_id):
        category = db.session.get(Category, category_id)
        if not category:
            abort(404, message="Category not found.", code="not_found")
        return category

    @blueprint.arguments(CategoryUpdateSchema)
    @blueprint.response(200, CategorySchema)
    def patch(self, data, category_id):
        category = db.session.get(Category, category_id)
        if not category:
            abort(404, message="Category not found.", code="not_found")
        for key, value in data.items():
            setattr(category, key, value)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="A category with this name already exists.", code="duplicate_category")
        return category

    @blueprint.response(204)
    def delete(self, category_id):
        category = db.session.get(Category, category_id)
        if not category:
            abort(404, message="Category not found.", code="not_found")
        if category.products:
            abort(409, message="Cannot delete a category referenced by products.", code="category_in_use")
        db.session.delete(category)
        db.session.commit()
        return "", 204
