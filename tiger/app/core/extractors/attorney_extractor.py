import re
from typing import Dict, Any

class AttorneyExtractor:
    """
    Extracts information about the legal counsel from a block of text.
    """

    def __init__(self):
        self.patterns = {
            "attorney_name": [re.compile(r"ATTORNEY FOR PLAINTIFF[S]?:\s*\n(.*)", re.IGNORECASE)],
            "firm_name": [re.compile(r"LAW OFFICES OF (.*)", re.IGNORECASE)],
            "bar_number": [re.compile(r"Bar No\.\s*(\d+)", re.IGNORECASE)],
            "address": [re.compile(r"(\d+\s+.*\s+Chicago,\s+IL\s+\d{5})", re.IGNORECASE)],
            "email": [re.compile(r"([\w\.-]+@[\w\.-]+)", re.IGNORECASE)],
            "phone_number": [re.compile(r"(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", re.IGNORECASE)],
        }

    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extracts attorney-related information from the text.

        Args:
            text: The unstructured text of a document.

        Returns:
            A dictionary containing the extracted attorney information.
        """
        results = {}
        for entity, patterns in self.patterns.items():
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    value = match.group(1) if match.groups() else match.group(0)
                    results[entity] = value.strip()
                    break
        return results
