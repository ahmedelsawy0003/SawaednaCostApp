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

    # --- START: الدالة الجديدة لجلب أسماء الشيتات ---
    def get_sheet_names(self):
        """
        يجلب قائمة بأسماء جميع الأوراق (الشيتات) في ملف Google Sheets المحدد.
        """
        try:
            spreadsheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            sheets = spreadsheet_metadata.get('sheets', [])
            sheet_names = [sheet.get('properties', {}).get('title', '') for sheet in sheets]
            return sheet_names, None # Success
        except Exception as e:
            return None, str(e) # Failure
    # --- END: الدالة الجديدة ---

    def read_data(self, range_name):
        """
        يقرأ البيانات من ورقة عمل محددة.
        """
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        return result.get("values", [])

    def write_data(self, base_sheet_name, values):
        """
        ينشئ ورقة عمل جديدة بتاريخ اليوم ويكتب البيانات فيها.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_sheet_name = f"{base_sheet_name} - {timestamp}"

        try:
            requests = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': new_sheet_name,
                            'rightToLeft': True
                        }
                    }
                }]
            }
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id, body=requests).execute()

            body = {"values": values}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, 
                range=new_sheet_name,
                valueInputOption="RAW", 
                body=body
            ).execute()
            
            return True, None
        
        except Exception as e:
            return False, str(e)