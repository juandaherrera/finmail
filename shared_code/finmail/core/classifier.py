"""
Classifier initialization.

Initializes the transaction classifier singleton with the Google Sheets
rule provider.
"""

from shared_code.finmail.core.config import settings
from shared_code.finmail.core.google_client import google_sheets_client
from shared_code.finmail.domain.classification import (
    GoogleSheetsRuleProvider,
    TransactionClassifier,
)

rule_provider = GoogleSheetsRuleProvider(
    google_sheets_client=google_sheets_client,
    spreadsheet_id=settings.GOOGLE_SPREADSHEET_IDENTIFIER,
    worksheet_name=settings.GOOGLE_CLASSIFICATION_WORKSHEET_NAME,
)

transaction_classifier = TransactionClassifier(rule_provider=rule_provider)
