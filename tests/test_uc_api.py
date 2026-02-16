"""Tests for Universal Credit API endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestUCCalculatorAPI:
    """Test UC calculator API endpoints."""

    def test_calculate_uc_basic(self, client):
        """Test basic UC calculation endpoint."""
        payload = {
            "claimant_type": "single",
            "claimant_age": 30,
            "monthly_rent": 600.00,
            "bedrooms_needed": 1,
            "housing_type": "renter",
            "assessment_month": "2026-02-01",
        }
        response = client.post("/api/uc/calculate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "claim_reference" in data
        assert data["claimant_type"] == "single"
        assert data["total_entitlement"] > 0

    def test_calculate_uc_with_children(self, client):
        """Test UC calculation with children."""
        payload = {
            "claimant_type": "single",
            "claimant_age": 30,
            "monthly_rent": 600.00,
            "bedrooms_needed": 2,
            "housing_type": "renter",
            "assessment_month": "2026-02-01",
            "children": [
                {"age": 8, "is_disabled": False},
                {"age": 5, "is_disabled": False},
            ],
        }
        response = client.post("/api/uc/calculate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["child_element"] > 0

    def test_calculate_uc_with_earnings(self, client):
        """Test UC calculation with earnings."""
        payload = {
            "claimant_type": "single",
            "claimant_age": 30,
            "monthly_rent": 600.00,
            "bedrooms_needed": 1,
            "housing_type": "renter",
            "assessment_month": "2026-02-01",
            "monthly_earnings": 500.00,
        }
        response = client.post("/api/uc/calculate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["earnings_deduction"] >= 0

    def test_calculate_uc_with_lha_rate(self, client):
        """Test UC calculation with LHA rate."""
        payload = {
            "claimant_type": "single",
            "claimant_age": 30,
            "monthly_rent": 900.00,
            "bedrooms_needed": 1,
            "housing_type": "renter",
            "brma_code": "E09000002",
            "assessment_month": "2026-02-01",
        }
        response = client.post("/api/uc/calculate", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Housing element should be capped at LHA rate (1100 for 1 bed London)
        assert data["housing_element"] <= 1100.00

    def test_get_lha_rate(self, client):
        """Test getting LHA rate."""
        response = client.get("/api/uc/lha-rate/E09000002?bedrooms=1")
        assert response.status_code == 200
        data = response.json()
        assert data["brma_code"] == "E09000002"
        assert data["bedrooms"] == 1
        assert data["monthly_rate"] > 0

    def test_get_lha_rate_invalid_brma(self, client):
        """Test getting LHA rate with invalid BRMA."""
        response = client.get("/api/uc/lha-rate/INVALID?bedrooms=1")
        assert response.status_code == 404

    def test_get_all_lha_rates(self, client):
        """Test getting all LHA rates for BRMA."""
        response = client.get("/api/uc/lha-rates/E09000002")
        assert response.status_code == 200
        data = response.json()
        assert data["brma_code"] == "E09000002"
        assert "rates" in data
        assert "one_bed_rate" in data["rates"]

    def test_calculate_uc_missing_required_field(self, client):
        """Test calculation fails with missing required field."""
        payload = {
            "claimant_type": "single",
            "claimant_age": 30,
            # missing monthly_rent
            "bedrooms_needed": 1,
            "housing_type": "renter",
            "assessment_month": "2026-02-01",
        }
        response = client.post("/api/uc/calculate", json=payload)
        assert response.status_code == 422

    def test_calculate_uc_invalid_claimant_type(self, client):
        """Test calculation fails with invalid claimant type."""
        payload = {
            "claimant_type": "invalid",
            "claimant_age": 30,
            "monthly_rent": 600.00,
            "bedrooms_needed": 1,
            "housing_type": "renter",
            "assessment_month": "2026-02-01",
        }
        response = client.post("/api/uc/calculate", json=payload)
        assert response.status_code == 422

    def test_calculate_uc_joint_claim(self, client):
        """Test UC calculation for joint claim."""
        payload = {
            "claimant_type": "joint",
            "claimant_age": 28,
            "partner_age": 26,
            "monthly_rent": 800.00,
            "bedrooms_needed": 2,
            "housing_type": "renter",
            "assessment_month": "2026-02-01",
        }
        response = client.post("/api/uc/calculate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["claimant_type"] == "joint"
        assert data["total_entitlement"] > 0

    def test_claim_reference_uniqueness(self, client):
        """Test that different calculations get different claim references."""
        payload = {
            "claimant_type": "single",
            "claimant_age": 30,
            "monthly_rent": 600.00,
            "bedrooms_needed": 1,
            "housing_type": "renter",
            "assessment_month": "2026-02-01",
        }
        response1 = client.post("/api/uc/calculate", json=payload)
        response2 = client.post("/api/uc/calculate", json=payload)

        data1 = response1.json()
        data2 = response2.json()

        assert data1["claim_reference"] != data2["claim_reference"]

    def test_claim_reference_format(self, client):
        """Test that claim reference follows expected format."""
        payload = {
            "claimant_type": "single",
            "claimant_age": 30,
            "monthly_rent": 600.00,
            "bedrooms_needed": 1,
            "housing_type": "renter",
            "assessment_month": "2026-02-01",
        }
        response = client.post("/api/uc/calculate", json=payload)
        data = response.json()

        # Claim reference should start with "UC-"
        assert data["claim_reference"].startswith("UC-")
