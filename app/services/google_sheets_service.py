import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

# نطاق الصلاحيات المطلوبة للوصول إلى Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

class GoogleSheetsService:
    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.service = self._authenticate()

    def _authenticate(self):
        """
        يصادق على الخدمة باستخدام بيانات الاعتماد من متغيرات البيئة.
        """
        creds_json_str = os.environ.get('GOOGLE_CREDENTIALS_JSON')
        
        if not creds_json_str:
            raise Exception("متغير البيئة GOOGLE_CREDENTIALS_JSON غير موجود.")

        creds_info = json.loads(creds_json_str)
        
        credentials = service_account.Credentials.from_service_account_info(
            creds_info, scopes=SCOPES
        )
        
        service = build("sheets", "v4", credentials=credentials)
        return service

    def read_data(self, range_name):
        """
        يقرأ البيانات من ورقة عمل محددة.
        """
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        return result.get("values", [])

    # START: Modified write function to create a new sheet each time
    def write_data(self, base_sheet_name, values):
        """
        ينشئ ورقة عمل جديدة بتاريخ اليوم ويكتب البيانات فيها.
        """
        # 1. Create a unique sheet name with the current date and time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_sheet_name = f"{base_sheet_name} - {timestamp}"

        try:
            # 2. Create the new sheet using the batchUpdate API
            requests = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': new_sheet_name,
                            'rightToLeft': True # Set sheet direction to RTL
                        }
                    }
                }]
            }
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id, body=requests).execute()

            # 3. Write the data to the newly created sheet
            body = {"values": values}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, 
                range=new_sheet_name,  # Use the new sheet name as the range
                valueInputOption="RAW", 
                body=body
            ).execute()
            
            return True, None # Success
        
        except Exception as e:
            # Check if the error is because the sheet already exists (highly unlikely but good practice)
            if 'already exists' in str(e):
                # Handle this case if needed, maybe by trying a different name
                pass
            return False, str(e) # Failure, return the error message
    # END: Modified write function