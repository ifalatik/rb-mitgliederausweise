# google.py
# this file contains the code to connect to Google Sheets using gspread and Google OAuth2 credentials.
from typing import Dict, List
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

# Constants for the Google Sheet and worksheet
SHEET_NAME = "Mitgliederliste"
WORKSHEET_INDEX = 3  # Index of the worksheet to access (0-based)
WORKSHEET_EXPECTED_HEADERS = [
        "Mitgliedsnummer",
        "Name",
        "Vorname",
        "Mitglieder-kategorie",
        "Hauptfunktion",
        "Adresse",
        "PLZ",
        "Ort",
        "Tel",
        "E-Mail",
        "Discord",
        "Geburtsdatum",
        "Datum Eintritt",
        "Datum Austritt",
        "Mitgliedsbeitrag",
        "IBAN",
        "BIC",
        "Institut",
        "Vereinbarung Abbuchung (Link)",
        "Beiträge gezahlt (J/N)"
    ]

def _get_gspread_client(service_account_file: str) -> gspread.Client:
    """
    Returns a gspread client authorized with the service account credentials.
    """
    creds = Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES
    )
    return gspread.authorize(creds)

def get_worksheet_data(service_account_file: str) -> List[Dict[str, int | float | str]]:
    """
    Fetches all records from the specified worksheet in the Google Sheet.

    Returns:
        List of dictionaries containing the worksheet data.
    """
    client = _get_gspread_client(service_account_file)
    sheet = client.open(SHEET_NAME).get_worksheet(WORKSHEET_INDEX)
    data = sheet.get_all_records(expected_headers=WORKSHEET_EXPECTED_HEADERS)
    return data
