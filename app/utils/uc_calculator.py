"""Universal Credit calculation engine."""
from datetime import date
from typing import Optional, List, Tuple
from decimal import Decimal, ROUND_HALF_UP


class UCRates:
    """2026-2027 Universal Credit rates (from April 2026)."""

    # Standard Allowance rates (monthly) - 2026-2027
    STANDARD_ALLOWANCE = {
        "single_under_25": 338.58,
        "single_25_plus": 424.90,
        "joint_under_25": 528.34,
        "joint_25_plus": 666.97,
    }

    # Child element rates (monthly) - 2026-2027
    FIRST_CHILD_ELEMENT = 284.89  # First or only child
    ADDITIONAL_CHILD_ELEMENT = 237.05  # Each additional child

    # Disabled child addition - estimated (not in public docs for 2026-27)
    DISABLED_CHILD_ADDITION = 137.45

    # Childcare costs
    CHILDCARE_PERCENTAGE = 0.85  # 85% of eligible childcare costs
    CHILDCARE_MAX_ONE_CHILD = 175.00  # Max eligible monthly costs
    CHILDCARE_MAX_TWO_PLUS = 300.00  # Max for 2+ children

    # Earnings taper and work allowance
    EARNINGS_TAPER = 0.55  # 55% taper rate
    WORK_ALLOWANCE_WITH_CHILDREN = 290.00  # Monthly
    WORK_ALLOWANCE_WITHOUT_CHILDREN = 0.00  # No work allowance if no children/disability

    # Disability and care elements
    WORK_ABILITY_ELEMENT = 134.88  # Limited capability for work
    WORK_AND_ACTIVITY_ELEMENT = 285.58  # Limited capability for work and activity
    CARER_ELEMENT = 163.44  # Carer addition


class UCCalculator:
    """Calculate Universal Credit entitlements."""

    def __init__(self, rates: Optional[UCRates] = None):
        """Initialize calculator with rates."""
        self.rates = rates or UCRates()

    def calculate(
        self,
        claimant_type: str,
        claimant_age: int,
        partner_age: Optional[int] = None,
        children: Optional[List[dict]] = None,
        monthly_earnings: float = 0.0,
        partner_monthly_earnings: float = 0.0,
        monthly_rent: float = 0.0,
        lha_rate: Optional[float] = None,
        has_work_allowance: bool = False,
        monthly_childcare_costs: float = 0.0,
        has_disability: bool = False,
        is_carer: bool = False,
    ) -> dict:
        """
        Calculate UC entitlement.

        Args:
            claimant_type: "single" or "joint"
            claimant_age: Age of main claimant
            partner_age: Age of partner (if joint claim)
            children: List of child dicts with 'age' and optional 'is_disabled'
            monthly_earnings: Claimant's net monthly earnings
            partner_monthly_earnings: Partner's net monthly earnings
            monthly_rent: Actual monthly rent paid
            lha_rate: LHA rate for the area/bedrooms (if not using actual rent)
            has_work_allowance: Whether claimant has work allowance
            monthly_childcare_costs: Eligible childcare costs
            has_disability: Whether claimant has disability
            is_carer: Whether claimant is a carer

        Returns:
            Dictionary with calculation breakdown
        """
        if children is None:
            children = []

        # Calculate standard allowance
        standard_allowance = self._calculate_standard_allowance(
            claimant_type, claimant_age, partner_age
        )

        # Calculate housing element
        housing_element = self._calculate_housing_element(monthly_rent, lha_rate)

        # Calculate child elements
        child_element = self._calculate_child_element(children)

        # Calculate childcare element
        childcare_element = self._calculate_childcare_element(
            monthly_childcare_costs, len(children)
        )

        # Calculate disability and carer elements
        disability_element = 0.0
        carer_element = 0.0
        if has_disability:
            disability_element = self.rates.WORK_ABILITY_ELEMENT
        if is_carer:
            carer_element = self.rates.CARER_ELEMENT

        # Calculate gross entitlement before earnings taper
        gross_entitlement = (
            standard_allowance
            + housing_element
            + child_element
            + childcare_element
            + disability_element
            + carer_element
        )

        # Calculate earnings deduction
        work_allowance = self._get_work_allowance(
            claimant_type, has_work_allowance, len(children), has_disability, is_carer
        )
        earnings_deduction = self._calculate_earnings_deduction(
            monthly_earnings, partner_monthly_earnings, work_allowance
        )

        # Calculate final entitlement
        total_entitlement = max(0.0, gross_entitlement - earnings_deduction)

        return {
            "standard_allowance": round(standard_allowance, 2),
            "housing_element": round(housing_element, 2),
            "child_element": round(child_element, 2),
            "childcare_element": round(childcare_element, 2),
            "disability_element": round(disability_element, 2),
            "carer_element": round(carer_element, 2),
            "gross_entitlement": round(gross_entitlement, 2),
            "work_allowance": round(work_allowance, 2),
            "total_earnings": round(monthly_earnings + partner_monthly_earnings, 2),
            "earnings_deduction": round(earnings_deduction, 2),
            "total_entitlement": round(total_entitlement, 2),
        }

    def _calculate_standard_allowance(
        self,
        claimant_type: str,
        claimant_age: int,
        partner_age: Optional[int] = None,
    ) -> float:
        """Calculate standard allowance based on claimant type and age."""
        if claimant_type == "single":
            if claimant_age < 25:
                return self.rates.STANDARD_ALLOWANCE["single_under_25"]
            else:
                return self.rates.STANDARD_ALLOWANCE["single_25_plus"]
        elif claimant_type == "joint":
            # For joint claims, use the lower of the two ages for age threshold
            min_age = min(claimant_age, partner_age or claimant_age)
            if min_age < 25:
                return self.rates.STANDARD_ALLOWANCE["joint_under_25"]
            else:
                return self.rates.STANDARD_ALLOWANCE["joint_25_plus"]
        else:
            raise ValueError(f"Invalid claimant type: {claimant_type}")

    def _calculate_housing_element(
        self, monthly_rent: float, lha_rate: Optional[float] = None
    ) -> float:
        """Calculate housing element (capped at LHA rate if provided)."""
        if lha_rate is None:
            return monthly_rent  # Use actual rent if no LHA rate provided
        # Housing element is the lower of actual rent and LHA rate
        return min(monthly_rent, lha_rate)

    def _calculate_child_element(self, children: List[dict]) -> float:
        """Calculate total child element for all children."""
        if not children:
            return 0.0

        total = 0.0
        for idx, child in enumerate(children):
            if idx == 0:
                total += self.rates.FIRST_CHILD_ELEMENT
            else:
                total += self.rates.ADDITIONAL_CHILD_ELEMENT

            # Add disabled child addition if applicable
            if child.get("is_disabled", False):
                total += self.rates.DISABLED_CHILD_ADDITION

        return total

    def _calculate_childcare_element(self, costs: float, num_children: int) -> float:
        """Calculate childcare element based on eligible costs."""
        if costs <= 0 or num_children == 0:
            return 0.0

        # Determine max eligible costs based on number of children
        max_costs = (
            self.rates.CHILDCARE_MAX_TWO_PLUS
            if num_children >= 2
            else self.rates.CHILDCARE_MAX_ONE_CHILD
        )
        eligible_costs = min(costs, max_costs)

        # Element is 85% of eligible costs
        return eligible_costs * self.rates.CHILDCARE_PERCENTAGE

    def _get_work_allowance(
        self,
        claimant_type: str,
        has_work_allowance: bool,
        num_children: int,
        has_disability: bool,
        is_carer: bool,
    ) -> float:
        """Determine work allowance amount."""
        # Work allowance applies if claimant has children, disability, or is carer
        if not (num_children > 0 or has_disability or is_carer):
            return 0.0

        if num_children > 0:
            return self.rates.WORK_ALLOWANCE_WITH_CHILDREN

        # For claimants with disability or carers without children
        # (simplified - actual rules are more complex)
        return self.rates.WORK_ALLOWANCE_WITH_CHILDREN

    def _calculate_earnings_deduction(
        self,
        monthly_earnings: float,
        partner_monthly_earnings: float = 0.0,
        work_allowance: float = 0.0,
    ) -> float:
        """Calculate how much UC is reduced by earnings."""
        total_earnings = monthly_earnings + partner_monthly_earnings

        if total_earnings <= work_allowance:
            return 0.0

        # Earnings above work allowance are tapered at 55%
        earnings_above_allowance = total_earnings - work_allowance
        return earnings_above_allowance * self.rates.EARNINGS_TAPER
