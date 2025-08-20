import os
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GoogleSheetsService:
    """خدمة التعامل مع Google Sheets API"""
    
    # نطاقات الوصول المطلوبة
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self):
        """تهيئة الخدمة"""
        self.creds = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """المصادقة مع Google API"""
        # التحقق من وجود ملف credentials.json
        if os.path.exists('credentials.json'):
            # استخدام OAuth2 للمصادقة
            if os.path.exists('token.json'):
                with open('token.json', 'r') as token:
                    self.creds = Credentials.from_authorized_user_info(json.load(token), self.SCOPES)
            
            # إذا لم تكن هناك بيانات اعتماد صالحة، فقم بإنشاء جديدة
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # حفظ بيانات الاعتماد للاستخدام لاحقاً
                with open('token.json', 'w') as token:
                    token.write(self.creds.to_json())
        
        # استخدام حساب الخدمة إذا كان متاحاً
        elif os.environ.get('GOOGLE_CREDENTIALS_JSON'):
             creds_json_string = os.environ.get('GOOGLE_CREDENTIALS_JSON')
             creds_info = json.loads(creds_json_string)
             self.creds = service_account.Credentials.from_service_account_info(
             creds_info, scopes=self.SCOPES)
      
      # إنشاء خدمة Google Sheets
        if self.creds:
            self.service = build('sheets', 'v4', credentials=self.creds)
    
    def create_spreadsheet(self, title):
        """إنشاء جدول بيانات جديد"""
        if not self.service:
            return None
        
        spreadsheet = {
            'properties': {
                'title': title
            },
            'sheets': [
                {
                    'properties': {
                        'title': 'بيانات المشروع'
                    }
                }
            ]
        }
        
        result = self.service.spreadsheets().create(body=spreadsheet).execute()
        return result.get('spreadsheetId')
    
    def setup_project_sheet(self, spreadsheet_id, project_data):
        """إعداد جدول البيانات للمشروع"""
        if not self.service:
            return False
        
        # إعداد معلومات المشروع
        project_info = [
            ["معلومات المشروع"],
            ["اسم المشروع", project_data.get('name', '')],
            ["مدير المشروع", project_data.get('manager', '')],
            ["موقع المشروع", project_data.get('location', '')],
            [""],
            ["بنود المشروع"]
        ]
        
        # إعداد عناوين الأعمدة
        headers = [
            "رقم البند", "وصف البند", "الوحدة", "الكمية التعاقدية", "التكلفة الإفرادية التعاقدية", 
            "التكلفة الإجمالية التعاقدية", "حالة البند", "الكمية الفعلية المنفذة", "التكلفة الإفرادية الفعلية", 
            "التكلفة الإجمالية الفعلية", "الوفر والزيادة للكميات", "تكلفة الوفر والزيادة", 
            "اسم المورد/المقاول", "طريقة التنفيذ", "المدفوع حتى تاريخه", "المتبقي", "ملاحظات"
        ]
        
        project_info.append(headers)
        
        # تحديث جدول البيانات
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='بيانات المشروع!A1',
            valueInputOption='USER_ENTERED',
            body={'values': project_info}
        ).execute()
        
        # تنسيق الجدول
        requests = [
            # تنسيق عنوان المشروع
            {
                'updateCells': {
                    'rows': [
                        {
                            'values': [
                                {
                                    'userEnteredFormat': {
                                        'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
                                        'textFormat': {'bold': True, 'fontSize': 14},
                                        'horizontalAlignment': 'CENTER'
                                    }
                                }
                            ]
                        }
                    ],
                    'fields': 'userEnteredFormat',
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': 1
                    }
                }
            },
            # تنسيق عناوين الأعمدة
            {
                'updateCells': {
                    'rows': [
                        {
                            'values': [
                                {
                                    'userEnteredFormat': {
                                        'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8},
                                        'textFormat': {'bold': True},
                                        'horizontalAlignment': 'CENTER'
                                    }
                                } for _ in range(len(headers))
                            ]
                        }
                    ],
                    'fields': 'userEnteredFormat',
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 5,
                        'endRowIndex': 6,
                        'startColumnIndex': 0,
                        'endColumnIndex': len(headers)
                    }
                }
            }
        ]
        
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
        
        return True
    
    def update_project_items(self, spreadsheet_id, items):
        """تحديث بنود المشروع في جدول البيانات"""
        if not self.service:
            return False
        
        # تحويل البنود إلى صفوف
        rows = []
        for item in items:
            row = [
                item.get('item_number', ''),
                item.get('description', ''),
                item.get('unit', ''),
                item.get('contract_quantity', 0),
                item.get('contract_unit_cost', 0),
                item.get('contract_total_cost', 0),
                item.get('status', 'نشط'),
                item.get('actual_quantity', ''),
                item.get('actual_unit_cost', ''),
                item.get('actual_total_cost', ''),
                item.get('quantity_variance', ''),
                item.get('cost_variance', ''),
                item.get('contractor_name', ''),
                item.get('execution_method', ''),
                item.get('paid_amount', 0),
                item.get('remaining_amount', ''),
                item.get('notes', '')
            ]
            rows.append(row)
        
        if rows:
            # تحديث جدول البيانات
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='بيانات المشروع!A7',
                valueInputOption='USER_ENTERED',
                body={'values': rows}
            ).execute()
        
        return True
    
    def get_project_items(self, spreadsheet_id):
        """استرجاع بنود المشروع من جدول البيانات"""
        if not self.service:
            return []
        
        # قراءة البيانات من الجدول
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='بيانات المشروع!A7:Q'
        ).execute()
        
        values = result.get('values', [])
        
        # تحويل البيانات إلى قائمة من القواميس
        items = []
        for row in values:
            if len(row) < 6:  # تخطي الصفوف غير المكتملة
                continue
                
            item = {
                'item_number': row[0] if len(row) > 0 else '',
                'description': row[1] if len(row) > 1 else '',
                'unit': row[2] if len(row) > 2 else '',
                'contract_quantity': float(row[3]) if len(row) > 3 and row[3] else 0,
                'contract_unit_cost': float(row[4]) if len(row) > 4 and row[4] else 0,
                'contract_total_cost': float(row[5]) if len(row) > 5 and row[5] else 0,
                'status': row[6] if len(row) > 6 else 'نشط',
                'actual_quantity': float(row[7]) if len(row) > 7 and row[7] else None,
                'actual_unit_cost': float(row[8]) if len(row) > 8 and row[8] else None,
                'actual_total_cost': float(row[9]) if len(row) > 9 and row[9] else None,
                'contractor_name': row[12] if len(row) > 12 else '',
                'execution_method': row[13] if len(row) > 13 else '',
                'paid_amount': float(row[14]) if len(row) > 14 and row[14] else 0,
                'notes': row[16] if len(row) > 16 else ''
            }
            items.append(item)
        
        return items