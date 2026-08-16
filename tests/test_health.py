def test_health(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_openapi_document(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/products/{product_id}/stock" in response.get_json()["paths"]
