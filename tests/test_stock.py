def test_stock_adjustments_create_newest_first_history(client, product):
    product_id = product["id"]
    added = client.post(
        f"/api/v1/products/{product_id}/stock",
        json={"quantity_change": 10, "reason": "Initial delivery"},
    )
    removed = client.post(
        f"/api/v1/products/{product_id}/stock",
        json={"quantity_change": -3, "reason": "Customer order"},
    )
    history = client.get(f"/api/v1/products/{product_id}/movements")

    assert added.get_json()["quantity"] == 10
    assert removed.get_json()["quantity"] == 7
    assert [movement["quantity_change"] for movement in history.get_json()] == [-3, 10]


def test_zero_and_insufficient_adjustments_are_rejected_without_movements(client, product):
    product_id = product["id"]
    zero = client.post(
        f"/api/v1/products/{product_id}/stock",
        json={"quantity_change": 0, "reason": "Invalid"},
    )
    insufficient = client.post(
        f"/api/v1/products/{product_id}/stock",
        json={"quantity_change": -1, "reason": "Order"},
    )

    assert zero.status_code == 400
    assert insufficient.status_code == 400
    assert client.get(f"/api/v1/products/{product_id}").get_json()["quantity"] == 0
    assert client.get(f"/api/v1/products/{product_id}/movements").get_json() == []
