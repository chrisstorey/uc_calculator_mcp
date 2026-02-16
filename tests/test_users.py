"""User endpoints tests."""


def test_create_user(client, sample_user):
    """Test user creation."""
    response = client.post("/api/users/", json=sample_user)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == sample_user["email"]
    assert data["username"] == sample_user["username"]
    assert "id" in data


def test_list_users(client):
    """Test listing users."""
    response = client.get("/api/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user(client, sample_user):
    """Test getting a specific user."""
    # Create user first
    create_response = client.post("/api/users/", json=sample_user)
    user_id = create_response.json()["id"]

    # Get user
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_get_user_not_found(client):
    """Test getting non-existent user."""
    response = client.get("/api/users/999")
    assert response.status_code == 404


def test_update_user(client, sample_user):
    """Test user update."""
    # Create user first
    create_response = client.post("/api/users/", json=sample_user)
    user_id = create_response.json()["id"]

    # Update user
    updated_data = {**sample_user, "full_name": "Updated User"}
    response = client.put(f"/api/users/{user_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated User"


def test_delete_user(client, sample_user):
    """Test user deletion."""
    # Create user first
    create_response = client.post("/api/users/", json=sample_user)
    user_id = create_response.json()["id"]

    # Delete user
    response = client.delete(f"/api/users/{user_id}")
    assert response.status_code == 204

    # Verify user is deleted
    get_response = client.get(f"/api/users/{user_id}")
    assert get_response.status_code == 404
