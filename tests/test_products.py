def test_product_crud_does_not_allow_direct_quantity_updates(client, category, product):
    product_id = product["id"]
    updated = client.patch(
        f"/api/v1/products/{product_id}",
        json={"name": "Quiet Keyboard", "quantity": 99},
    )

    assert updated.status_code == 422
    unchanged = client.get(f"/api/v1/products/{product_id}").get_json()
    assert unchanged["name"] == "Mechanical Keyboard"
    assert unchanged["quantity"] == 0


def test_product_validation_duplicate_and_missing_category(client, category, product):
    negative = client.post(
        "/api/v1/products",
        json={"sku": "BAD", "name": "Bad", "price": "-1", "category_id": category["id"]},
    )
    duplicate = client.post(
        "/api/v1/products",
        json={"sku": product["sku"], "name": "Other", "price": "1", "category_id": category["id"]},
    )
    missing_category = client.post(
        "/api/v1/products",
        json={"sku": "NEW", "name": "Other", "price": "1", "category_id": 999},
    )

    assert negative.status_code == 422
    assert duplicate.status_code == 409
    assert missing_category.status_code == 404


def test_product_search_filter_sort_and_pagination(client, category, product):
    client.post(
        "/api/v1/products",
        json={"sku": "MOU-001", "name": "Wireless Mouse", "price": "29.99", "category_id": category["id"]},
    )

    search = client.get("/api/v1/products?search=mouse")
    priced = client.get("/api/v1/products?min_price=50&sort=-price&page=1&per_page=1")
    low_stock = client.get("/api/v1/products?low_stock=true")

    assert [item["sku"] for item in search.get_json()["items"]] == ["MOU-001"]
    assert [item["sku"] for item in priced.get_json()["items"]] == ["KEY-001"]
    assert priced.get_json()["pagination"] == {"page": 1, "pages": 1, "per_page": 1, "total": 1}
    assert len(low_stock.get_json()["items"]) == 2


def test_product_query_validation(client):
    response = client.get("/api/v1/products?min_price=invalid&per_page=101&sort=unknown")

    assert response.status_code == 422
    assert response.get_json()["error"]["details"]["query"]


def test_product_delete_and_missing_resource(client, product):
    response = client.delete(f"/api/v1/products/{product['id']}")

    assert response.status_code == 204
    assert client.get(f"/api/v1/products/{product['id']}").status_code == 404
