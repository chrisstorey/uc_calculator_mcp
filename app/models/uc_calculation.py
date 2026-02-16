"""Universal Credit calculation model."""
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, Enum, ForeignKey, JSON
from datetime import datetime
import enum
from app.database.base import Base


class ClaimantType(str, enum.Enum):
    """Claimant type enumeration."""

    SINGLE = "single"
    JOINT = "joint"


class HousingType(str, enum.Enum):
    """Housing type enumeration."""

    OWNER_OCCUPIER = "owner_occupier"
    RENTER = "renter"
    SOCIAL_HOUSING = "social_housing"


class ChildBenefit(str, enum.Enum):
    """Child benefit enumeration."""

    RESPONSIBLE = "responsible"
    SHARED_CARE = "shared_care"


class UCClaim(Base):
    """Model for Universal Credit claims and calculations."""

    __tablename__ = "uc_claims"

    id = Column(Integer, primary_key=True, index=True)
    # Claim reference - unique identifier
    claim_reference = Column(String(50), unique=True, index=True, nullable=False)
    # Claimant details
    claimant_type = Column(Enum(ClaimantType), nullable=False)
    claimant_age = Column(Integer, nullable=False)
    partner_age = Column(Integer, nullable=True)  # For joint claims
    # Children details - stored as JSON for flexibility
    children = Column(JSON, default=list)  # List of {age, benefit_type}
    # Housing
    housing_type = Column(Enum(HousingType), nullable=False)
    bedrooms_needed = Column(Integer, nullable=False)
    monthly_rent = Column(Float, nullable=False)  # Actual rent paid
    brma_code = Column(String(50), ForeignKey("lha_rates.brma_code"), nullable=True)
    # Work and earnings
    monthly_earnings = Column(Float, default=0.0)
    partner_monthly_earnings = Column(Float, default=0.0, nullable=True)
    has_work_allowance = Column(Boolean, default=False)
    has_childcare_costs = Column(Boolean, default=False)
    monthly_childcare_costs = Column(Float, default=0.0)
    has_disability = Column(Boolean, default=False)
    is_carer = Column(Boolean, default=False)
    # Calculation period
    assessment_month = Column(Date, nullable=False)
    # Results - all amounts in GBP
    standard_allowance = Column(Float, nullable=True)
    housing_element = Column(Float, nullable=True)
    child_element = Column(Float, nullable=True)
    childcare_element = Column(Float, nullable=True)
    disability_element = Column(Float, nullable=True)
    carer_element = Column(Float, nullable=True)
    earnings_deduction = Column(Float, nullable=True)
    total_entitlement = Column(Float, nullable=True)
    # Metadata
    calculated_at = Column(Date, default=datetime.utcnow)
    notes = Column(String(1000), nullable=True)

    class Config:
        from_attributes = True
