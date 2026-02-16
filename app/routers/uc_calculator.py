"""Universal Credit calculator API routes."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import date
import uuid

from app.schemas.uc_calculation import (
    UCCalculationRequest,
    UCCalculationResult,
    LHARateResponse,
)
from app.models.uc_calculation import UCClaim
from app.models.lha_rates import LHARate
from app.database.session import get_db
from app.utils.uc_calculator import UCCalculator
from app.utils.lha_service import LHAService

router = APIRouter()
calculator = UCCalculator()


@router.post("/calculate", response_model=UCCalculationResult)
def calculate_uc(
    request: UCCalculationRequest,
    db: Session = Depends(get_db),
) -> UCCalculationResult:
    """
    Calculate Universal Credit entitlement.

    This endpoint calculates a UC entitlement based on claimant circumstances.
    """
    # Get LHA rate if BRMA code provided
    lha_rate = None
    if request.brma_code:
        lha_rate = LHAService.get_lha_rate(
            request.brma_code,
            request.bedrooms_needed,
            request.assessment_month,
        )

    # Perform calculation
    calculation_result = calculator.calculate(
        claimant_type=request.claimant_type.value,
        claimant_age=request.claimant_age,
        partner_age=request.partner_age,
        children=[
            {
                "age": child.age,
                "is_disabled": child.is_disabled,
            }
            for child in request.children
        ],
        monthly_earnings=request.monthly_earnings,
        partner_monthly_earnings=request.partner_monthly_earnings,
        monthly_rent=request.monthly_rent,
        lha_rate=lha_rate,
        has_work_allowance=request.has_work_allowance,
        monthly_childcare_costs=request.monthly_childcare_costs,
        has_disability=request.has_disability,
        is_carer=request.is_carer,
    )

    # Generate unique claim reference
    claim_reference = f"UC-{uuid.uuid4().hex[:8].upper()}"

    # Store in database
    db_claim = UCClaim(
        claim_reference=claim_reference,
        claimant_type=request.claimant_type.value,
        claimant_age=request.claimant_age,
        partner_age=request.partner_age,
        children=[
            {"age": child.age, "is_disabled": child.is_disabled}
            for child in request.children
        ],
        housing_type=request.housing_type.value,
        bedrooms_needed=request.bedrooms_needed,
        monthly_rent=request.monthly_rent,
        brma_code=request.brma_code,
        monthly_earnings=request.monthly_earnings,
        partner_monthly_earnings=request.partner_monthly_earnings,
        has_work_allowance=request.has_work_allowance,
        has_childcare_costs=request.has_childcare_costs,
        monthly_childcare_costs=request.monthly_childcare_costs,
        has_disability=request.has_disability,
        is_carer=request.is_carer,
        assessment_month=request.assessment_month,
        standard_allowance=calculation_result["standard_allowance"],
        housing_element=calculation_result["housing_element"],
        child_element=calculation_result["child_element"],
        childcare_element=calculation_result["childcare_element"],
        disability_element=calculation_result["disability_element"],
        carer_element=calculation_result["carer_element"],
        earnings_deduction=calculation_result["earnings_deduction"],
        total_entitlement=calculation_result["total_entitlement"],
    )
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)

    return UCCalculationResult(
        claim_reference=claim_reference,
        claimant_type=request.claimant_type.value,
        claimant_age=request.claimant_age,
        standard_allowance=calculation_result["standard_allowance"],
        housing_element=calculation_result["housing_element"],
        child_element=calculation_result["child_element"],
        childcare_element=calculation_result["childcare_element"],
        disability_element=calculation_result["disability_element"],
        carer_element=calculation_result["carer_element"],
        earnings_deduction=calculation_result["earnings_deduction"],
        total_entitlement=calculation_result["total_entitlement"],
        assessment_month=request.assessment_month,
        calculated_at=date.today(),
    )


@router.get("/lha-rate/{brma_code}")
def get_lha_rate(
    brma_code: str,
    bedrooms: int = 1,
) -> dict:
    """
    Get LHA rate for a BRMA.

    Args:
        brma_code: Broad Rental Market Area code
        bedrooms: Number of bedrooms (default: 1)
    """
    rate = LHAService.get_lha_rate(brma_code, bedrooms)
    if rate is None:
        raise HTTPException(
            status_code=404,
            detail=f"LHA rate not found for BRMA {brma_code}",
        )
    return {
        "brma_code": brma_code,
        "bedrooms": bedrooms,
        "monthly_rate": rate,
    }


@router.get("/lha-rates/{brma_code}")
def get_all_lha_rates(brma_code: str) -> dict:
    """Get all LHA rates for a BRMA."""
    rates = LHAService.get_lha_rates_for_brma(brma_code)
    if rates is None:
        raise HTTPException(
            status_code=404,
            detail=f"BRMA {brma_code} not found",
        )
    return {"brma_code": brma_code, "rates": rates}


@router.post("/lookup-postcode/{postcode}")
def lookup_brma_by_postcode(postcode: str) -> dict:
    """
    Look up BRMA code by postcode.

    Note: This is a placeholder. In production, this should use
    the official ONS postcode to BRMA lookup service.
    """
    brma_code = LHAService.search_brma_by_postcode(postcode)
    if brma_code is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could not find BRMA for postcode {postcode}",
        )
    return {
        "postcode": postcode,
        "brma_code": brma_code,
    }


@router.get("/calculation/{claim_reference}", response_model=UCCalculationResult)
def get_calculation(
    claim_reference: str,
    db: Session = Depends(get_db),
) -> UCCalculationResult:
    """Retrieve a previously calculated UC entitlement."""
    claim = db.query(UCClaim).filter(
        UCClaim.claim_reference == claim_reference
    ).first()

    if not claim:
        raise HTTPException(
            status_code=404,
            detail=f"Calculation {claim_reference} not found",
        )

    return UCCalculationResult.from_orm(claim)
