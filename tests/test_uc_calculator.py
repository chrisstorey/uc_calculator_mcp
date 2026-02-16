"""Tests for Universal Credit calculator."""
import pytest
from app.utils.uc_calculator import UCCalculator, UCRates


class TestUCCalculator:
    """Test Universal Credit calculation logic."""

    @pytest.fixture
    def calculator(self):
        """Create calculator instance."""
        return UCCalculator()

    def test_single_under_25_standard_allowance(self, calculator):
        """Test standard allowance for single person under 25."""
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=22,
            monthly_rent=500,
        )
        assert result["standard_allowance"] == UCRates.STANDARD_ALLOWANCE["single_under_25"]

    def test_single_25_plus_standard_allowance(self, calculator):
        """Test standard allowance for single person 25 and over."""
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=30,
            monthly_rent=500,
        )
        assert result["standard_allowance"] == UCRates.STANDARD_ALLOWANCE["single_25_plus"]

    def test_joint_under_25_standard_allowance(self, calculator):
        """Test standard allowance for joint claim with at least one under 25."""
        result = calculator.calculate(
            claimant_type="joint",
            claimant_age=22,
            partner_age=25,
            monthly_rent=500,
        )
        assert result["standard_allowance"] == UCRates.STANDARD_ALLOWANCE["joint_under_25"]

    def test_joint_25_plus_standard_allowance(self, calculator):
        """Test standard allowance for joint claim both 25 and over."""
        result = calculator.calculate(
            claimant_type="joint",
            claimant_age=26,
            partner_age=28,
            monthly_rent=500,
        )
        assert result["standard_allowance"] == UCRates.STANDARD_ALLOWANCE["joint_25_plus"]

    def test_housing_element_uses_actual_rent(self, calculator):
        """Test that housing element uses actual rent when no LHA provided."""
        monthly_rent = 600.00
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=30,
            monthly_rent=monthly_rent,
        )
        assert result["housing_element"] == monthly_rent

    def test_housing_element_capped_at_lha(self, calculator):
        """Test that housing element is capped at LHA rate."""
        monthly_rent = 900.00
        lha_rate = 700.00
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=30,
            monthly_rent=monthly_rent,
            lha_rate=lha_rate,
        )
        assert result["housing_element"] == lha_rate

    def test_single_child_element(self, calculator):
        """Test child element for single child."""
        children = [{"age": 8, "is_disabled": False}]
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=30,
            children=children,
            monthly_rent=500,
        )
        assert result["child_element"] == UCRates.FIRST_CHILD_ELEMENT

    def test_two_children_element(self, calculator):
        """Test child element for two children."""
        children = [
            {"age": 8, "is_disabled": False},
            {"age": 5, "is_disabled": False},
        ]
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=30,
            children=children,
            monthly_rent=500,
        )
        expected = (
            UCRates.FIRST_CHILD_ELEMENT + UCRates.ADDITIONAL_CHILD_ELEMENT
        )
        assert result["child_element"] == expected

    def test_disabled_child_addition(self, calculator):
        """Test child element includes disabled child addition."""
        children = [{"age": 8, "is_disabled": True}]
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=30,
            children=children,
            monthly_rent=500,
        )
        expected = UCRates.FIRST_CHILD_ELEMENT + UCRates.DISABLED_CHILD_ADDITION
        assert result["child_element"] == expected

    def test_no_earnings_deduction_below_work_allowance(self, calculator):
        """Test no earnings deduction when earnings below work allowance."""
        children = [{"age": 8, "is_disabled": False}]
        monthly_earnings = 200.00  # Below work allowance
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=30,
            children=children,
            monthly_earnings=monthly_earnings,
            monthly_rent=500,
        )
        assert result["earnings_deduction"] == 0.0

    def test_earnings_deduction_above_work_allowance(self, calculator):
        """Test earnings deduction at 55% taper."""
        children = [{"age": 8, "is_disabled": False}]
        monthly_earnings = 500.00
        work_allowance = 290.00  # With children
        above_allowance = monthly_earnings - work_allowance
        expected_deduction = above_allowance * 0.55
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=30,
            children=children,
            monthly_earnings=monthly_earnings,
            monthly_rent=500,
        )
        assert abs(result["earnings_deduction"] - expected_deduction) < 0.01

    def test_no_work_allowance_without_children_or_disability(self, calculator):
        """Test no work allowance for single person without children/disability."""
        monthly_earnings = 500.00
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=30,
            monthly_earnings=monthly_earnings,
            monthly_rent=500,
        )
        # All earnings should be tapered at 55%
        expected_deduction = monthly_earnings * 0.55
        assert abs(result["earnings_deduction"] - expected_deduction) < 0.01

    def test_childcare_element_one_child(self, calculator):
        """Test childcare element calculation for one child."""
        children = [{"age": 3, "is_disabled": False}]
        monthly_childcare = 150.00
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=30,
            children=children,
            monthly_childcare_costs=monthly_childcare,
            monthly_rent=500,
        )
        # 85% of costs, capped at max for one child
        expected = monthly_childcare * 0.85
        assert abs(result["childcare_element"] - expected) < 0.01

    def test_childcare_element_two_children(self, calculator):
        """Test childcare element is capped higher for two children."""
        children = [
            {"age": 3, "is_disabled": False},
            {"age": 5, "is_disabled": False},
        ]
        monthly_childcare = 400.00
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=30,
            children=children,
            monthly_childcare_costs=monthly_childcare,
            monthly_rent=500,
        )
        # Capped at 300 for 2+ children, then 85%
        expected = 300.00 * 0.85
        assert abs(result["childcare_element"] - expected) < 0.01

    def test_disability_element(self, calculator):
        """Test disability element is added."""
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=30,
            has_disability=True,
            monthly_rent=500,
        )
        assert result["disability_element"] == UCRates.WORK_ABILITY_ELEMENT

    def test_carer_element(self, calculator):
        """Test carer element is added."""
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=30,
            is_carer=True,
            monthly_rent=500,
        )
        assert result["carer_element"] == UCRates.CARER_ELEMENT

    def test_total_entitlement_calculation(self, calculator):
        """Test total entitlement is calculated correctly."""
        children = [{"age": 8, "is_disabled": False}]
        monthly_earnings = 200.00
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=30,
            children=children,
            monthly_earnings=monthly_earnings,
            monthly_rent=600,
        )
        expected_total = (
            result["standard_allowance"]
            + result["housing_element"]
            + result["child_element"]
            + result["childcare_element"]
            + result["disability_element"]
            + result["carer_element"]
            - result["earnings_deduction"]
        )
        assert abs(result["total_entitlement"] - expected_total) < 0.01

    def test_total_entitlement_not_negative(self, calculator):
        """Test that total entitlement is never negative."""
        monthly_earnings = 5000.00  # Very high earnings
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=30,
            monthly_earnings=monthly_earnings,
            monthly_rent=500,
        )
        assert result["total_entitlement"] >= 0

    def test_complex_scenario(self, calculator):
        """Test complex scenario with multiple elements."""
        children = [
            {"age": 8, "is_disabled": False},
            {"age": 5, "is_disabled": True},
        ]
        result = calculator.calculate(
            claimant_type="single",
            claimant_age=28,
            children=children,
            monthly_earnings=400.00,
            monthly_rent=750.00,
            lha_rate=700.00,
            monthly_childcare_costs=200.00,
            has_disability=False,
            is_carer=False,
        )
        # Verify all components are calculated
        assert result["standard_allowance"] > 0
        assert result["housing_element"] > 0
        assert result["child_element"] > 0
        assert result["childcare_element"] > 0
        assert result["earnings_deduction"] > 0
        assert result["total_entitlement"] >= 0


class TestLHAService:
    """Test LHA service."""

    def test_get_lha_rate_by_bedrooms(self):
        """Test getting LHA rate for specific bedrooms."""
        from app.utils.lha_service import LHAService

        rate = LHAService.get_lha_rate("E09000002", bedrooms=1)
        assert rate is not None
        assert rate > 0

    def test_get_lha_rates_for_brma(self):
        """Test getting all LHA rates for BRMA."""
        from app.utils.lha_service import LHAService

        rates = LHAService.get_lha_rates_for_brma("E09000002")
        assert rates is not None
        assert "one_bed_rate" in rates
        assert "two_bed_rate" in rates

    def test_invalid_brma_returns_none(self):
        """Test that invalid BRMA returns None."""
        from app.utils.lha_service import LHAService

        rate = LHAService.get_lha_rate("INVALID", bedrooms=1)
        assert rate is None
