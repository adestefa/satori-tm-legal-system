from typing import Dict, List

class FinancialExtractor:
    """
    Identifies financial institutions and credit reporting agencies mentioned in the text.
    """

    def __init__(self):
        self.financial_institutions = [
            "JPMorgan Chase", "Bank of America", "Wells Fargo", "Citigroup",
            "Goldman Sachs", "Morgan Stanley", "U.S. Bancorp", "PNC Financial Services",
            "Capital One", "TD Bank", "Bank of New York Mellon", "State Street",
            "American Express", "Discover Financial"
        ]
        self.credit_bureaus = ["Experian", "TransUnion", "Equifax"]

    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extracts financial institution and credit bureau names from the text.

        Args:
            text: The unstructured text of a document.

        Returns:
            A dictionary containing lists of found institutions and bureaus.
        """
        results = {
            "financial_institutions": [],
            "credit_bureaus": [],
        }
        text_lower = text.lower()

        for institution in self.financial_institutions:
            if institution.lower() in text_lower:
                results["financial_institutions"].append(institution)

        for bureau in self.credit_bureaus:
            if bureau.lower() in text_lower:
                results["credit_bureaus"].append(bureau)

        return results
