"""Google client initialization."""

from shared_code.finmail.clients import GoogleSheetsClient
from shared_code.finmail.core.config import settings

google_sheets_client = GoogleSheetsClient(settings.GOOGLE_JSON_KEY)
