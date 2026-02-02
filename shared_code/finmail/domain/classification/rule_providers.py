"""
Rule providers module.

Contains the RuleProvider protocol and implementations for loading
classification rules from various sources.
"""

import logging
from typing import Protocol

from shared_code.finmail.clients import GoogleSheetsClient
from shared_code.finmail.domain.classification.classification_rules import (
    ClassificationRule,
)

logger = logging.getLogger(__name__)


class RuleProvider(Protocol):
    """
    Protocol for rule providers.

    Rule providers are responsible for loading classification rules from a
    specific source. This protocol enables dependency injection and allows
    for easy switching between different rule sources (e.g., Google Sheets,
    database, config file).
    """

    def get_rules(self) -> list[ClassificationRule]:
        """
        Load and return classification rules.

        Returns
        -------
        list[ClassificationRule]
            A list of classification rules.
        """
        ...


class GoogleSheetsRuleProvider:
    """
    Rule provider that loads classification rules from Google Sheets.

    Expected sheet structure:
    - Column 1: conditions (expression, e.g., "merchant:.*uber.*" or
                "pocket:.*Rappi.* AND description:.*food.*")
    - Column 2: category (target category)

    The first row is treated as headers and skipped.
    """

    def __init__(
        self,
        google_sheets_client: GoogleSheetsClient,
        spreadsheet_id: str,
        worksheet_name: str,
    ):
        """
        Initialize the Google Sheets rule provider.

        Parameters
        ----------
        google_sheets_client : GoogleSheetsClient
            The Google Sheets client to use for reading rules.
        spreadsheet_id : str
            The ID or URL of the spreadsheet containing rules.
        worksheet_name : str
            The name of the worksheet containing rules.
        """
        self.google_sheets_client = google_sheets_client
        self.spreadsheet_id = spreadsheet_id
        self.worksheet_name = worksheet_name

    def get_rules(self) -> list[ClassificationRule]:
        """
        Load classification rules from Google Sheets.

        Returns
        -------
        list[ClassificationRule]
            A list of classification rules loaded from the sheet.
        """
        try:
            rows = self.google_sheets_client.read_all(
                spreadsheet_identifier=self.spreadsheet_id,
                worksheet_name=self.worksheet_name,
            )

            # Skip header row
            data_rows = rows[1:] if len(rows) > 1 else []

            rules = []
            for idx, row in enumerate(data_rows, start=2):  # Start at 2
                # Skip empty rows
                if not row or all(not cell.strip() for cell in row):
                    continue

                # Ensure row has at least 2 columns
                expected_columns = 2
                if len(row) < expected_columns:
                    logger.warning(
                        "Skipping row %d: insufficient columns (expected %d, got %d)",
                        idx,
                        expected_columns,
                        len(row),
                    )
                    continue

                conditions = row[0].strip()
                category = row[1].strip()

                # Skip rows with empty required fields
                if not conditions or not category:
                    logger.warning("Skipping row %d: empty required field(s)", idx)
                    continue

                try:
                    rule = ClassificationRule(
                        conditions=conditions,
                        category=category,
                    )
                    rules.append(rule)
                except ValueError as e:
                    logger.error(
                        "Error parsing rule at row %d: %s. Skipping.",
                        idx,
                        e,
                    )
                    continue

            logger.info("Loaded %d classification rules from Google Sheets", len(rules))
            return rules

        except Exception as e:
            logger.error(
                "Failed to load classification rules from Google Sheets: %s", e
            )
            return []
