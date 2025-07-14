import pytest
from app.core.extractors.court_extractor import CourtExtractor
from app.core.extractors.party_extractor import PartyExtractor
from app.core.extractors.attorney_extractor import AttorneyExtractor
from app.core.extractors.financial_extractor import FinancialExtractor

@pytest.fixture
def sample_text():
    return """
IN THE UNITED STATES DISTRICT COURT
FOR THE NORTHERN DISTRICT OF ILLINOIS
EASTERN DIVISION

JOHN DOE,
    Plaintiff,

v.

EQUIFAX INFORMATION SERVICES LLC,
    Defendant.

Case No. 1:23-cv-01234
COMPLAINT FOR DAMAGES

ATTORNEY FOR PLAINTIFF:
Jane Smith
LAW OFFICES OF JANE SMITH
123 Main Street, Chicago, IL 60601
Bar No. 1234567
(312) 555-1212
jane.smith@example.com

This case involves inaccurate information provided by Capital One.
"""

def test_court_extractor(sample_text):
    extractor = CourtExtractor()
    results = extractor.extract(sample_text)
    assert results["jurisdiction"] == "IN THE UNITED STATES DISTRICT COURT"
    assert results["division"] == "EASTERN DIVISION"
    assert results["case_number"] == "1:23-cv-01234"
    assert results["case_classification"] == "COMPLAINT FOR DAMAGES"

def test_party_extractor(sample_text):
    extractor = PartyExtractor()
    results = extractor.extract(sample_text)
    assert results["plaintiffs"] == ["JOHN DOE"]
    assert results["defendants"] == ["EQUIFAX INFORMATION SERVICES LLC"]

def test_attorney_extractor(sample_text):
    extractor = AttorneyExtractor()
    results = extractor.extract(sample_text)
    assert results["attorney_name"] == "Jane Smith"
    assert results["firm_name"] == "JANE SMITH"
    assert results["bar_number"] == "1234567"
    assert results["address"] == "123 Main Street, Chicago, IL 60601"
    assert results["email"] == "jane.smith@example.com"
    assert results["phone_number"] == "(312) 555-1212"

def test_financial_extractor(sample_text):
    extractor = FinancialExtractor()
    results = extractor.extract(sample_text)
    assert "Capital One" in results["financial_institutions"]
    assert "Equifax" in results["credit_bureaus"]
