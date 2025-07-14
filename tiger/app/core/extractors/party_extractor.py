import re
from typing import Dict, List

class PartyExtractor:
    """
    Identifies the plaintiffs and defendants in the case from a block of text.
    """

    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extracts plaintiff and defendant names from the text.

        Args:
            text: The unstructured text of a document.

        Returns:
            A dictionary containing lists of plaintiffs and defendants.
        """
        plaintiffs = []
        defendants = []

        # Find the block between the court info and the case number
        main_block_match = re.search(r"DIVISION\s*\n(.*?)\n\s*Case No\.", text, re.DOTALL | re.IGNORECASE)
        if not main_block_match:
            return {"plaintiffs": plaintiffs, "defendants": defendants}

        main_block = main_block_match.group(1)

        # Split the block by 'v.' or 'vs.'
        parts = re.split(r'\n\s*v\.s?\s*\n', main_block, flags=re.IGNORECASE)
        if len(parts) != 2:
            return {"plaintiffs": plaintiffs, "defendants": defendants}

        plaintiff_block, defendant_block = parts

        # Clean up and extract names
        plaintiffs = self._clean_block(plaintiff_block)
        defendants = self._clean_block(defendant_block)

        return {"plaintiffs": plaintiffs, "defendants": defendants}

    def _clean_block(self, block: str) -> List[str]:
        """Cleans a block of text and extracts names."""
        names = []
        lines = block.split('\n')
        for line in lines:
            if 'plaintiff' in line.lower() or 'defendant' in line.lower():
                continue
            # Remove commas and extra whitespace
            name = line.replace(',', '').strip()
            if name:
                names.append(name)
        return names
