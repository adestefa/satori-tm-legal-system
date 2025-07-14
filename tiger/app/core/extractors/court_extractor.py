import re
from typing import Dict, Any

class CourtExtractor:
    """
    Extracts information related to the court and case filing from a block of text.
    """

    def __init__(self):
        self.patterns = {
            "jurisdiction": [
                re.compile(r"IN THE UNITED STATES DISTRICT COURT[^\n]*", re.IGNORECASE),
                re.compile(r"IN THE SUPERIOR COURT OF[^\n]*", re.IGNORECASE),
                re.compile(r"IN THE CIRCUIT COURT OF[^\n]*", re.IGNORECASE),
            ],
            "division": [
                re.compile(r"DIVISION: (.*)", re.IGNORECASE),
                re.compile(r"(\w+\s+DIVISION)", re.IGNORECASE),
            ],
            "case_number": [
                re.compile(r"Case No\. (.*)", re.IGNORECASE),
                re.compile(r"CASE NUMBER: (.*)", re.IGNORECASE),
                re.compile(r"\d{1,2}[-:\.]\d{2,4}[-:\.]\w{2,6}[-:\.]\d{4,6}", re.IGNORECASE),
            ],
            "case_classification": [
                re.compile(r"CIVIL ACTION", re.IGNORECASE),
                re.compile(r"COMPLAINT FOR DAMAGES", re.IGNORECASE),
            ],
        }

    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extracts court-related information from the text.

        Args:
            text: The unstructured text of a document.

        Returns:
            A dictionary containing the extracted court information.
        """
        results = {}
        for entity, patterns in self.patterns.items():
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    # Extract the most relevant group, or the full match
                    value = match.group(1) if match.groups() else match.group(0)
                    results[entity] = value.strip()
                    break  # Move to the next entity once a match is found
        return results
