"""Service for managing LHA rates."""
from datetime import date
from typing import Optional
import requests


class LHAService:
    """Service for LHA rate lookups and management."""

    # Official GOV.UK LHA rates API endpoint
    LHA_API_ENDPOINT = "https://lha-direct.voa.gov.uk/api"

    # Sample LHA rates for 2026-2027 (populated from various sources)
    # These are typical rates - actual rates should be fetched from official sources
    DEFAULT_LHA_RATES = {
        "E92000001": {  # Yorkshire and The Humber
            "brma_name": "North Yorkshire",
            "local_authority": "North Yorkshire Council",
            "studio_rate": 600.00,
            "one_bed_rate": 700.00,
            "two_bed_rate": 850.00,
            "three_bed_rate": 1000.00,
            "four_bed_rate": 1200.00,
        },
        "E08000032": {  # West Yorkshire
            "brma_name": "Bradford",
            "local_authority": "Bradford Council",
            "studio_rate": 550.00,
            "one_bed_rate": 650.00,
            "two_bed_rate": 800.00,
            "three_bed_rate": 950.00,
            "four_bed_rate": 1150.00,
        },
        "E08000016": {  # West Midlands
            "brma_name": "Birmingham",
            "local_authority": "Birmingham City Council",
            "studio_rate": 550.00,
            "one_bed_rate": 700.00,
            "two_bed_rate": 850.00,
            "three_bed_rate": 1000.00,
            "four_bed_rate": 1200.00,
        },
        "E09000002": {  # London (Barnet)
            "brma_name": "London",
            "local_authority": "Barnet Council",
            "studio_rate": 950.00,
            "one_bed_rate": 1100.00,
            "two_bed_rate": 1350.00,
            "three_bed_rate": 1600.00,
            "four_bed_rate": 1900.00,
        },
    }

    @staticmethod
    def get_lha_rate(
        brma_code: Optional[str] = None,
        bedrooms: int = 1,
        assessment_date: Optional[date] = None,
    ) -> Optional[float]:
        """
        Get LHA rate for a BRMA and bedroom count.

        Args:
            brma_code: BRMA code
            bedrooms: Number of bedrooms (1-4)
            assessment_date: Date for rate lookup (uses current rates if not specified)

        Returns:
            Monthly LHA rate or None if not found
        """
        if not brma_code or brma_code not in LHAService.DEFAULT_LHA_RATES:
            return None

        rates = LHAService.DEFAULT_LHA_RATES[brma_code]

        # Map bedrooms to rate key
        if bedrooms == 0:
            rate_key = "studio_rate"
        elif bedrooms == 1:
            rate_key = "one_bed_rate"
        elif bedrooms == 2:
            rate_key = "two_bed_rate"
        elif bedrooms == 3:
            rate_key = "three_bed_rate"
        elif bedrooms >= 4:
            rate_key = "four_bed_rate"
        else:
            return None

        return rates.get(rate_key)

    @staticmethod
    def get_lha_rates_for_brma(brma_code: str) -> Optional[dict]:
        """Get all LHA rates for a BRMA."""
        if brma_code not in LHAService.DEFAULT_LHA_RATES:
            return None
        return LHAService.DEFAULT_LHA_RATES[brma_code]

    @staticmethod
    def search_brma_by_postcode(postcode: str) -> Optional[str]:
        """
        Search for BRMA code by postcode.

        Note: This would require integration with the official
        ONS postcode to BRMA lookup service.
        """
        # Placeholder implementation
        # In production, this would call the official API
        postcode_upper = postcode.upper().replace(" ", "")

        # Very simplified mapping - in production use proper API
        london_prefixes = ["SW", "SE", "E", "W", "N", "NW", "N"]
        if any(postcode_upper.startswith(p) for p in london_prefixes):
            return "E09000002"  # London

        return None

    @staticmethod
    def fetch_lha_rates_from_gov():
        """
        Fetch latest LHA rates from government API.

        This would be implemented to fetch from the official
        LHA Direct API or government publications.
        """
        # Placeholder for future implementation
        # Would call lha-direct.voa.gov.uk or gov.uk API
        pass
