import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# نطاق الصلاحيات المطلوبة للوصول إلى Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

class GoogleSheetsService:
    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.service = self._authenticate()

    def _authenticate(self):
        """
        يصادق على الخدمة باستخدام بيانات الاعتماد من متغيرات البيئة.
        هذه الطريقة مصممة للعمل على خوادم مثل Vercel.
        """
        # قراءة بيانات الاعتماد من متغير البيئة الذي قمت بتعيينه في Vercel
        creds_json_str = os.environ.get('GOOGLE_CREDENTIALS_JSON')
        
        if not creds_json_str:
            raise Exception("متغير البيئة GOOGLE_CREDENTIALS_JSON غير موجود.")

        # تحويل النص (JSON string) إلى قاموس (dictionary)
        creds_info = json.loads(creds_json_str)
        
        # إنشاء كائن بيانات الاعتماد
        credentials = service_account.Credentials.from_service_account_info(
            creds_info, scopes=SCOPES
        )
        
        # بناء كائن الخدمة
        service = build("sheets", "v4", credentials=credentials)
        return service

    def read_data(self, range_name):
        """
        يقرأ البيانات من ورقة عمل محددة.
        """
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        return result.get("values", [])

    def write_data(self, range_name, values):
        """
        يكتب البيانات في ورقة عمل محددة.
        """
        # مسح البيانات القديمة قبل الكتابة (اختياري لكنه مفيد للتصدير)
        self.service.spreadsheets().values().clear(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
            
        body = {"values": values}
        result = self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id, range=range_name,
            valueInputOption="RAW", body=body).execute()
        return result