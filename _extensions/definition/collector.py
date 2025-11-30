"""
DefinitionsCollector - Stores and validates term definitions.

Collects definitions during the build process, checks for duplicates,
and merges with standard glossary entries.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

__all__ = [
    'DuplicateTermError',
    'DefinitionEntry',
    'DefinitionsCollector',
]


class DuplicateTermError(Exception):
    """Raised when a term is defined multiple times."""

    def __init__(self, term: str, locations: List[str]):
        self.term = term
        self.locations = locations
        message = f"Duplicate term '{term}' defined in:\n"
        for loc in locations:
            message += f"  - {loc}\n"
        super().__init__(message)


@dataclass
class DefinitionEntry:
    """A single term definition."""
    term: str
    definition: str
    docname: str
    lineno: int
    anchor: str

    @property
    def location(self) -> str:
        """Human-readable location string."""
        return f"{self.docname}:{self.lineno}"


class DefinitionsCollector:
    """Collects and validates term definitions across the build."""

    def __init__(self, case_sensitive: bool = False):
        """
        Initialize the collector.

        Args:
            case_sensitive: If False, "Term" and "term" are considered duplicates
        """
        self.case_sensitive = case_sensitive
        self.definitions: Dict[str, DefinitionEntry] = {}

    def _normalize_term(self, term: str) -> str:
        """Normalize a term for comparison."""
        if self.case_sensitive:
            return term.strip()
        return term.strip().lower()

    def add_definition(
        self,
        term: str,
        definition: str,
        docname: str,
        lineno: int,
        anchor: str,
    ) -> None:
        """
        Add a definition, checking for duplicates.

        Args:
            term: The term being defined
            definition: The definition text
            docname: Document name where defined
            lineno: Line number in source
            anchor: HTML anchor ID

        Raises:
            DuplicateTermError: If term already defined
        """
        normalized = self._normalize_term(term)

        if normalized in self.definitions:
            existing = self.definitions[normalized]
            raise DuplicateTermError(
                term,
                [existing.location, f"{docname}:{lineno}"]
            )

        self.definitions[normalized] = DefinitionEntry(
            term=term,
            definition=definition,
            docname=docname,
            lineno=lineno,
            anchor=anchor,
        )

    def check_against_std_glossary(self, std_terms: Dict[str, tuple]) -> None:
        """
        Check for conflicts with standard {glossary} entries.

        Args:
            std_terms: Dict from env.domaindata['std']['terms']
                       Format: {term: (docname, labelid)} (Sphinx 7+)
                       Legacy: {term: (docname, labelid, term_text)}

        Raises:
            DuplicateTermError: If any inline definition conflicts with std glossary
        """
        for normalized, entry in self.definitions.items():
            # Check if term exists in standard glossary
            if normalized in std_terms:
                data = std_terms[normalized]
                std_docname = data[0]
                raise DuplicateTermError(
                    entry.term,
                    [
                        f"{entry.docname}:{entry.lineno} (inline definition)",
                        f"{std_docname} (standard glossary)",
                    ]
                )

    def get_all_definitions(self) -> List[DefinitionEntry]:
        """Get all definitions sorted alphabetically by term."""
        return sorted(
            self.definitions.values(),
            key=lambda e: e.term.lower()
        )

    def get_definition(self, term: str) -> Optional[DefinitionEntry]:
        """Get a specific definition by term."""
        normalized = self._normalize_term(term)
        return self.definitions.get(normalized)

    def __len__(self) -> int:
        return len(self.definitions)

    def __contains__(self, term: str) -> bool:
        return self._normalize_term(term) in self.definitions
