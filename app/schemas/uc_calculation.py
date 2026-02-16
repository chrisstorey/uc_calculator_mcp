"""Pydantic schemas for Universal Credit calculation."""
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from enum import Enum


class ClaimantType(str, Enum):
    """Claimant type."""

    SINGLE = "single"
    JOINT = "joint"


class HousingType(str, Enum):
    """Housing type."""

    OWNER_OCCUPIER = "owner_occupier"
    RENTER = "renter"
    SOCIAL_HOUSING = "social_housing"


class ChildInfo(BaseModel):
    """Child information."""

    age: int = Field(..., ge=0, le=20)
    is_disabled: bool = False


class UCCalculationRequest(BaseModel):
    """Request schema for UC calculation."""

    # Claimant info
    claimant_type: ClaimantType = Field(...)
    claimant_age: int = Field(..., ge=16, le=120)
    partner_age: Optional[int] = Field(None, ge=16, le=120)
    children: List[ChildInfo] = Field(default_factory=list)
    # Housing
    housing_type: HousingType = Field(...)
    bedrooms_needed: int = Field(..., ge=1, le=5)
    monthly_rent: float = Field(..., ge=0)
    brma_code: Optional[str] = None
    # Work and earnings
    monthly_earnings: float = Field(default=0, ge=0)
    partner_monthly_earnings: Optional[float] = Field(default=0, ge=0)
    has_work_allowance: bool = False
    # Additional elements
    has_childcare_costs: bool = False
    monthly_childcare_costs: float = Field(default=0, ge=0)
    has_disability: bool = False
    is_carer: bool = False
    # Assessment period
    assessment_month: date = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "claimant_type": "single",
                "claimant_age": 35,
                "children": [],
                "housing_type": "renter",
                "bedrooms_needed": 1,
                "monthly_rent": 600.00,
                "brma_code": "E92000001",
                "monthly_earnings": 200.00,
                "has_work_allowance": True,
                "assessment_month": "2026-02-01",
            }
        }


class UCCalculationResult(BaseModel):
    """Result schema for UC calculation."""

    claim_reference: str
    claimant_type: str
    claimant_age: int
    standard_allowance: float
    housing_element: float
    child_element: float = 0.0
    childcare_element: float = 0.0
    disability_element: float = 0.0
    carer_element: float = 0.0
    earnings_deduction: float
    total_entitlement: float
    assessment_month: date
    calculated_at: date

    class Config:
        from_attributes = True


class LHARateResponse(BaseModel):
    """LHA rate response."""

    brma_code: str
    brma_name: str
    local_authority: str
    effective_from: date
    studio_rate: Optional[float] = None
    one_bed_rate: float
    two_bed_rate: float
    three_bed_rate: float
    four_bed_rate: float

    class Config:
        from_attributes = True
