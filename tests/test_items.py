"""Item endpoints tests."""


def test_create_item(client, sample_item):
    """Test item creation."""
    response = client.post("/api/items/", json=sample_item)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == sample_item["title"]
    assert "id" in data


def test_list_items(client):
    """Test listing items."""
    response = client.get("/api/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_item(client, sample_item):
    """Test getting a specific item."""
    # Create item first
    create_response = client.post("/api/items/", json=sample_item)
    item_id = create_response.json()["id"]

    # Get item
    response = client.get(f"/api/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id


def test_get_item_not_found(client):
    """Test getting non-existent item."""
    response = client.get("/api/items/999")
    assert response.status_code == 404


def test_update_item(client, sample_item):
    """Test item update."""
    # Create item first
    create_response = client.post("/api/items/", json=sample_item)
    item_id = create_response.json()["id"]

    # Update item
    updated_data = {**sample_item, "price": 19.99}
    response = client.put(f"/api/items/{item_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["price"] == 19.99


def test_delete_item(client, sample_item):
    """Test item deletion."""
    # Create item first
    create_response = client.post("/api/items/", json=sample_item)
    item_id = create_response.json()["id"]

    # Delete item
    response = client.delete(f"/api/items/{item_id}")
    assert response.status_code == 204

    # Verify item is deleted
    get_response = client.get(f"/api/items/{item_id}")
    assert get_response.status_code == 404
