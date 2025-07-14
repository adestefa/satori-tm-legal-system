"""
Unified JSON Schema for Tiger-Monkey Hydrated JSON
This is the single source of truth for hydrated JSON format used by both Tiger and Monkey.
This schema is based on the ground truth example: test-data/test-json/ground_truth_complaint.json
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class CaseInformation(BaseModel):
    court_name: str
    court_district: str
    case_number: str
    document_title: str
    document_type: str = "FCRA"

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str

class Plaintiff(BaseModel):
    name: str
    address: Address
    residency: str
    consumer_status: str

class Defendant(BaseModel):
    name: str
    short_name: str
    type: str
    state_of_incorporation: str
    business_status: str

class Parties(BaseModel):
    plaintiff: Plaintiff
    defendants: List[Defendant]

class Jurisdiction(BaseModel):
    basis: str
    citation: str

class JurisdictionAndVenue(BaseModel):
    federal_jurisdiction: Jurisdiction
    supplemental_jurisdiction: Jurisdiction
    venue: Jurisdiction

class FactualBackground(BaseModel):
    """Enhanced factual background with numbered allegations."""
    summary: Optional[str] = Field(None, description="Brief summary of case facts")
    allegations: List[str] = Field(default=[], description="Numbered factual allegations")
    preliminary_statement: Optional[str] = Field(None, description="Preliminary case statement")

class LegalClaim(BaseModel):
    """Individual legal violation claim with interactive selection capability."""
    citation: str = Field(..., description="Statutory citation (e.g., '15 U.S.C. § 1681i')")
    description: str = Field(..., description="Full description of the legal violation")
    selected: bool = Field(default=False, description="Whether lawyer has selected this claim")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="AI confidence score")
    category: str = Field(..., description="Claim category (FCRA, NY_FCRA, etc.)")
    against_defendants: Optional[List[str]] = Field(default=[], description="Applicable defendant short names")

class Allegation(BaseModel):
    citation: str
    description: str
    against_defendants: Optional[List[str]] = None

class CauseOfAction(BaseModel):
    """Legal cause of action with interactive claims."""
    count_number: int = Field(..., description="Sequential cause number (1, 2, 3...)")
    title: str = Field(..., description="Cause of action title")
    against_defendants: List[str] = Field(..., description="Defendant short names")
    legal_claims: List[LegalClaim] = Field(default=[], description="Associated legal claims")

class PrayerForRelief(BaseModel):
    damages: List[str]
    injunctive_relief: List[str]
    costs_and_fees: List[str]

class FilingDetails(BaseModel):
    date: str
    signature_date: str

class Metadata(BaseModel):
    tiger_case_id: str
    format_version: str

class HydratedJSON(BaseModel):
    case_information: CaseInformation
    parties: Parties
    jurisdiction_and_venue: JurisdictionAndVenue
    preliminary_statement: str
    factual_background: FactualBackground
    causes_of_action: List[CauseOfAction]
    prayer_for_relief: PrayerForRelief
    jury_demand: bool
    filing_details: FilingDetails
    metadata: Metadata

def validate_hydrated_json(data: Dict[str, Any]) -> tuple[bool, Optional[Dict], Optional[List[str]]]:
    """Validates a dictionary against the HydratedJSON schema."""
    try:
        HydratedJSON(**data)
        return True, None, None
    except Exception as e:
        return False, e.errors(), None

__all__ = ["HydratedJSON", "validate_hydrated_json"]