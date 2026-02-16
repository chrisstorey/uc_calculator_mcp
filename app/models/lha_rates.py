"""LHA (Local Housing Allowance) rates database model."""
from sqlalchemy import Column, Integer, String, Float, Date
from app.database.base import Base


class LHARate(Base):
    """Model for Local Housing Allowance rates by BRMA and bedroom count."""

    __tablename__ = "lha_rates"

    id = Column(Integer, primary_key=True, index=True)
    # Broad Rental Market Area code/name
    brma_code = Column(String(50), index=True, nullable=False)
    brma_name = Column(String(255), nullable=False)
    # Region or local authority
    local_authority = Column(String(255), nullable=False)
    # Effective date for these rates
    effective_from = Column(Date, nullable=False, index=True)
    effective_to = Column(Date, nullable=True)
    # Bedroom counts and their corresponding rates (monthly)
    studio_rate = Column(Float, nullable=True)  # Studio/bedsit
    one_bed_rate = Column(Float, nullable=False)
    two_bed_rate = Column(Float, nullable=False)
    three_bed_rate = Column(Float, nullable=False)
    four_bed_rate = Column(Float, nullable=False)

    class Config:
        from_attributes = True
