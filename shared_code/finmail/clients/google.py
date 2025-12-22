"""Google Sheets client for Finmail."""

import re

import gspread
from google.oauth2.service_account import Credentials
from gspread import Worksheet

from shared_code.finmail.models import Transaction


def _extract_spreadsheet_id(spreadsheet_identifier: str) -> str:
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", spreadsheet_identifier)
    if match:
        return match.group(1)
    return spreadsheet_identifier


class GoogleSheetsClient:
    """Client to interact with Google Sheets using service account credentials."""

    def __init__(self, google_json_key: str):
        """
        Initialize the client with the specified Google JSON key.

        Parameters
        ----------
        google_json_key : str, optional
            The name of the environment variable containing the Google service account
            JSON key. Defaults to "GOOGLE_JSON_KEY".

        Attributes
        ----------
        google_json_key : str
            Stores the name of the environment variable for the JSON key.
        client : object
            The authorized Google client instance.
        """
        self._google_json_key = google_json_key
        self.client = self._authorize()

    def _authorize(self) -> gspread.Client:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(
            self._google_json_key, scopes=scopes
        )
        return gspread.authorize(creds)

    def open_sheet(
        self, spreadsheet_identifier: str, worksheet_name: str | None = None
    ) -> gspread.Worksheet:
        """
        Open a Google Sheets spreadsheet and returns the specified worksheet.

        Parameters
        ----------
        spreadsheet_identifier : str
            The ID or URL of the Google Sheets spreadsheet to open.
        worksheet_name : str or None, optional
            The name of the worksheet to open within the spreadsheet. If None, the first
            worksheet (sheet1) is returned.

        Returns
        -------
        gspread.Worksheet
            The requested worksheet object from the opened spreadsheet.
        """
        spreadsheet_id = _extract_spreadsheet_id(spreadsheet_identifier)
        spreadsheet = self.client.open_by_key(spreadsheet_id)
        return (
            spreadsheet.worksheet(worksheet_name)
            if worksheet_name
            else spreadsheet.sheet1
        )

    @staticmethod
    def get_last_filled_row(sheet: Worksheet, column: int = 1) -> int:
        """
        Get the index of the last filled row in a specified Google Sheets worksheet.

        Parameters
        ----------
        sheet : gspread.Worksheet
            The worksheet object to check for the last filled row.
        column : int, optional
            The column number to check for filled rows.
                Defaults to 1 (the first column).

        Returns
        -------
        int
            The index of the last filled row in the worksheet.
        """
        column_values = sheet.col_values(column)
        return len(column_values)

    def append_row(
        self,
        spreadsheet_identifier: str,
        row_values: list,
        worksheet_name: str | None = None,
    ) -> bool:
        """
        Append a row of values to a specified worksheet in a Google Spreadsheet.

        Parameters
        ----------
        spreadsheet_identifier : str
            The ID or URL of the Google Spreadsheet to append the row to.
        row_values : list
            The list of values to append as a new row in the worksheet.
        worksheet_name : str or None, optional
            The name of the worksheet within the spreadsheet. If None, the default
            worksheet is used.

        Returns
        -------
        bool
            True if the row was appended successfully, otherwise False.
        """
        sheet = self.open_sheet(spreadsheet_identifier, worksheet_name)
        first_empty_row = self.get_last_filled_row(sheet) + 1
        sheet.insert_row(row_values, index=first_empty_row)
        return True

    def read_all(
        self, spreadsheet_identifier: str, worksheet_name: str | None = None
    ) -> list[list]:
        """
        Read all values from a specified Google Sheets worksheet.

        Parameters
        ----------
        spreadsheet_identifier : str
            The ID or URL of the Google Spreadsheet to access.
        worksheet_name : str or None, optional
            The name of the worksheet within the spreadsheet. If None, the default
            worksheet is used.

        Returns
        -------
        list of list
            A list of rows, where each row is represented as a list of cell values.
        """
        sheet = self.open_sheet(spreadsheet_identifier, worksheet_name)
        return sheet.get_all_values()

    def clear_sheet(
        self, spreadsheet_identifier: str, worksheet_name: str | None = None
    ) -> bool:
        """
        Clear all data from the specified worksheet in a Google Spreadsheet.

        Parameters
        ----------
        spreadsheet_identifier : str
            The ID or URL of the Google Spreadsheet to access.
        worksheet_name : str or None, optional
            The name of the worksheet to clear. If None, the default worksheet is used.

        Returns
        -------
        bool
            True if the worksheet was cleared successfully.
        """
        sheet = self.open_sheet(spreadsheet_identifier, worksheet_name)
        sheet.clear()
        return True

    def insert_transaction(
        self,
        spreadsheet_identifier: str,
        transaction: Transaction,
        worksheet_name: str | None = None,
    ) -> bool:
        """
        Insert a transaction into the specified Google Sheets worksheet.

        Parameters
        ----------
        spreadsheet_identifier : str
            The ID or URL of the Google Spreadsheet to insert the transaction into.
        transaction : Transaction
            The Transaction object containing the data to insert.
        worksheet_name : str or None, optional
            The name of the worksheet within the spreadsheet. If None, the default
            worksheet is used.

        Returns
        -------
        bool
            True if the transaction was inserted successfully.
        """
        formatted_date = transaction.date_local.strftime("%d/%m/%Y %H:%M:%S")
        # TODO @juandaherrera: move this to a mapper utility
        row_values = [
            formatted_date,
            transaction.pocket,
            transaction.category,
            transaction.currency,
            transaction.amount,
            # TODO @juandaherrera: we need to fix this blank column (it has a formula)
            "",
            transaction.description,
        ]
        return self.append_row(spreadsheet_identifier, row_values, worksheet_name)
