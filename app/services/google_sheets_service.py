import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

class GoogleSheetsService:
    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # This part would typically require user interaction in a web app
                # For a Vercel deployment, you'd need to handle OAuth flow differently
                # (e.g., using environment variables for credentials or a pre-authorized token)
                # For now, we'll assume credentials.json is available for local testing
                if os.path.exists("credentials.json"):
                    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    raise Exception("credentials.json not found. Please provide Google API credentials.")
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)
        return build("sheets", "v4", credentials=creds)

    def read_data(self, range_name):
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        return result.get("values", [])

    def write_data(self, range_name, values):
        body = {"values": values}
        result = self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id, range=range_name,
            valueInputOption="RAW", body=body).execute()
        return result


