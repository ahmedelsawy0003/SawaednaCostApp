from flask import Blueprint, request, jsonify, redirect, url_for, flash
from app.models.project import Project
from app.models.item import Item
from app.services.google_sheets_service import GoogleSheetsService
from app.extensions import db

sheets_bp = Blueprint('sheets', __name__, url_prefix='/sheets')

@sheets_bp.route('/project/<int:project_id>/create', methods=['POST'])
def create_sheet(project_id):
    """إنشاء جدول بيانات جديد للمشروع"""
    project = Project.query.get_or_404(project_id)
    
    # إنشاء خدمة Google Sheets
    sheets_service = GoogleSheetsService()
    
    # إنشاء جدول بيانات جديد
    spreadsheet_id = sheets_service.create_spreadsheet(f"مشروع {project.name}")
    
    if not spreadsheet_id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'فشل في إنشاء جدول البيانات'}), 500
        flash('فشل في إنشاء جدول البيانات', 'error')
        return redirect(url_for('project.get_project', project_id=project_id))
    
    # تحديث معرف جدول البيانات في المشروع
    project.spreadsheet_id = spreadsheet_id
    db.session.commit()
    
    # إعداد جدول البيانات للمشروع
    sheets_service.setup_project_sheet(spreadsheet_id, project.to_dict())
    
    # مزامنة بنود المشروع مع جدول البيانات
    items = Item.query.filter_by(project_id=project_id).all()
    sheets_service.update_project_items(spreadsheet_id, [item.to_dict() for item in items])
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'message': 'تم إنشاء جدول البيانات بنجاح',
            'spreadsheet_id': spreadsheet_id,
            'url': f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        })
    
    flash('تم إنشاء جدول البيانات بنجاح', 'success')
    return redirect(url_for('project.get_project', project_id=project_id))

@sheets_bp.route('/project/<int:project_id>/sync', methods=['POST'])
def sync_project(project_id):
    """مزامنة بيانات المشروع مع Google Sheets"""
    project = Project.query.get_or_404(project_id)
    
    # التحقق من وجود معرف جدول البيانات
    if not project.spreadsheet_id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'لم يتم ربط المشروع بجدول بيانات'}), 400
        flash('لم يتم ربط المشروع بجدول بيانات', 'error')
        return redirect(url_for('project.get_project', project_id=project_id))
    
    # إنشاء خدمة Google Sheets
    sheets_service = GoogleSheetsService()
    
    # مزامنة بنود المشروع مع جدول البيانات
    items = Item.query.filter_by(project_id=project_id).all()
    result = sheets_service.update_project_items(project.spreadsheet_id, [item.to_dict() for item in items])
    
    if not result:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'فشل في مزامنة البيانات'}), 500
        flash('فشل في مزامنة البيانات', 'error')
        return redirect(url_for('project.get_project', project_id=project_id))
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'message': 'تم مزامنة البيانات بنجاح'})
    
    flash('تم مزامنة البيانات بنجاح', 'success')
    return redirect(url_for('project.get_project', project_id=project_id))

@sheets_bp.route('/project/<int:project_id>/import', methods=['POST'])
def import_from_sheet(project_id):
    """استيراد بيانات من Google Sheets إلى المشروع"""
    project = Project.query.get_or_404(project_id)
    
    # التحقق من وجود معرف جدول البيانات
    if not project.spreadsheet_id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'لم يتم ربط المشروع بجدول بيانات'}), 400
        flash('لم يتم ربط المشروع بجدول بيانات', 'error')
        return redirect(url_for('project.get_project', project_id=project_id))
    
    # إنشاء خدمة Google Sheets
    sheets_service = GoogleSheetsService()
    
    # استيراد بنود المشروع من جدول البيانات
    sheet_items = sheets_service.get_project_items(project.spreadsheet_id)
    
    if not sheet_items:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'لم يتم العثور على بيانات في جدول البيانات'}), 404
        flash('لم يتم العثور على بيانات في جدول البيانات', 'error')
        return redirect(url_for('project.get_project', project_id=project_id))
    
    # تحديث البنود الموجودة وإضافة بنود جديدة
    for sheet_item in sheet_items:
        # البحث عن البند بواسطة رقم البند
        item = Item.query.filter_by(project_id=project_id, item_number=sheet_item['item_number']).first()
        
        if item:
            # تحديث البند الموجود
            item.description = sheet_item['description']
            item.unit = sheet_item['unit']
            item.contract_quantity = sheet_item['contract_quantity']
            item.contract_unit_cost = sheet_item['contract_unit_cost']
            item.contract_total_cost = sheet_item['contract_total_cost']
            item.status = sheet_item['status']
            
            if sheet_item['actual_quantity'] is not None:
                item.actual_quantity = sheet_item['actual_quantity']
                item.actual_unit_cost = sheet_item['actual_unit_cost']
                item.actual_total_cost = sheet_item['actual_total_cost']
            
            item.contractor_name = sheet_item['contractor_name']
            item.execution_method = sheet_item['execution_method']
            item.paid_amount = sheet_item['paid_amount']
            item.notes = sheet_item['notes']
        else:
            # إنشاء بند جديد
            new_item = Item(
                project_id=project_id,
                item_number=sheet_item['item_number'],
                description=sheet_item['description'],
                unit=sheet_item['unit'],
                contract_quantity=sheet_item['contract_quantity'],
                contract_unit_cost=sheet_item['contract_unit_cost'],
                contract_total_cost=sheet_item['contract_total_cost'],
                status=sheet_item['status'],
                actual_quantity=sheet_item['actual_quantity'],
                actual_unit_cost=sheet_item['actual_unit_cost'],
                actual_total_cost=sheet_item['actual_total_cost'],
                contractor_name=sheet_item['contractor_name'],
                execution_method=sheet_item['execution_method'],
                paid_amount=sheet_item['paid_amount'],
                notes=sheet_item['notes']
            )
            db.session.add(new_item)
    
    # حفظ التغييرات
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'message': 'تم استيراد البيانات بنجاح', 'count': len(sheet_items)})
    
    flash(f'تم استيراد {len(sheet_items)} بند بنجاح', 'success')
    return redirect(url_for('item.get_items', project_id=project_id))

@sheets_bp.route('/project/<int:project_id>/url', methods=['GET'])
def get_sheet_url(project_id):
    """الحصول على رابط جدول البيانات"""
    project = Project.query.get_or_404(project_id)
    
    if not project.spreadsheet_id:
        return jsonify({'error': 'لم يتم ربط المشروع بجدول بيانات'}), 404
    
    return jsonify({
        'spreadsheet_id': project.spreadsheet_id,
        'url': f"https://docs.google.com/spreadsheets/d/{project.spreadsheet_id}"
    })