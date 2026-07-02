from flask_jwt_extended import get_jwt_identity

from app import db
from app.models.category import Category
from app.schemas.category_schema import CategorySchema
from app.utils.responses import success_response, error_response

category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)

def list_categories():
    user_id = int(get_jwt_identity())
    categories = Category.query.filter_by(user_id=user_id).order_by(Category.name).all()
    if not categories:
        return success_response(
            data={"categories": []},
            message="No categories found",
        )
    return success_response(
        data={"categories": categories_schema.dump(categories)},
        message="Categories retrieved successfully",
    )