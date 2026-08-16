def test_category_crud(client):
    created = client.post("/api/v1/categories", json={"name": "Hardware"})
    category_id = created.get_json()["id"]

    assert created.status_code == 201
    assert client.get(f"/api/v1/categories/{category_id}").get_json()["name"] == "Hardware"

    updated = client.patch(f"/api/v1/categories/{category_id}", json={"name": "Components"})
    assert updated.status_code == 200
    assert updated.get_json()["name"] == "Components"

    assert client.delete(f"/api/v1/categories/{category_id}").status_code == 204
    assert client.get(f"/api/v1/categories/{category_id}").status_code == 404


def test_category_validation_and_duplicate_conflict(client, category):
    invalid = client.post("/api/v1/categories", json={"name": ""})
    duplicate = client.post("/api/v1/categories", json={"name": category["name"]})

    assert invalid.status_code == 422
    assert invalid.get_json()["error"]["details"]
    assert duplicate.status_code == 409
    assert duplicate.get_json()["error"]["code"] == "duplicate_category"


def test_category_with_products_cannot_be_deleted(client, category, product):
    response = client.delete(f"/api/v1/categories/{category['id']}")

    assert response.status_code == 409
    assert response.get_json()["error"]["code"] == "category_in_use"
