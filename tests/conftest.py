import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app(tmp_path):
    database_path = tmp_path / "test.db"
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path.as_posix()}",
        }
    )
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def category(client):
    response = client.post(
        "/api/v1/categories",
        json={"name": "Peripherals", "description": "Computer accessories"},
    )
    return response.get_json()


@pytest.fixture
def product(client, category):
    response = client.post(
        "/api/v1/products",
        json={
            "sku": "KEY-001",
            "name": "Mechanical Keyboard",
            "price": "79.99",
            "category_id": category["id"],
        },
    )
    return response.get_json()
