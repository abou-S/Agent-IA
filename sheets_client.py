import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from config import GOOGLE_SHEETS_SPREADSHEET_ID, CATEGORY_TO_SHEET

# Portée nécessaire pour écrire dans Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

CREDENTIALS_FILE = "credentials.json"      # le même que pour Gmail
TOKEN_SHEETS_FILE = "token_sheets.json"    # sera créé automatiquement


def get_sheets_service():
    """
    Crée un client Google Sheets avec OAuth (comme pour Gmail).
    Utilise credentials.json + token_sheets.json.
    """
    creds = None

    if os.path.exists(TOKEN_SHEETS_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_SHEETS_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_SHEETS_FILE, "w") as token:
            token.write(creds.to_json())

    service = build("sheets", "v4", credentials=creds)
    return service


def append_ticket_row(category_key: str, sujet: str, urgence: str, synthese: str):
    """
    Ajoute une ligne dans l’onglet correspondant à la catégorie.
    Colonnes : Sujet | Urgence | Synthèse
    """
    service = get_sheets_service()
    sheet_name = CATEGORY_TO_SHEET[category_key]

    # Quotes obligatoires (à cause des espaces / accents dans le nom du sheet)
    range_name = f"'{sheet_name}'!A:C"
    values = [[sujet, urgence, synthese]]

    body = {
        "values": values
    }

    print(f"[SHEETS] Ajout dans '{sheet_name}' : {sujet} | {urgence}")  # debug

    request = service.spreadsheets().values().append(
        spreadsheetId=GOOGLE_SHEETS_SPREADSHEET_ID,
        range=range_name,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    )
    request.execute()


