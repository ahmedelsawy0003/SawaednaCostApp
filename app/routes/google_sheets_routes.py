<<<<<<< HEAD
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
=======
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.google_sheets_service import GoogleSheetsService
from app.models.project import Project
from app.models.item import Item
from app.extensions import db
from flask_login import login_required

sheets_bp = Blueprint("sheets", __name__)

@sheets_bp.route("/projects/<int:project_id>/export_items", methods=["POST"])
@login_required
def export_project(project_id):
    project = Project.query.get_or_404(project_id)
    if not project.spreadsheet_id:
        flash("لا يوجد معرّف Google Sheets لهذا المشروع.", "danger")
        return redirect(url_for("project.get_project", project_id=project_id))

    try:
        service = GoogleSheetsService(project.spreadsheet_id)
        items = Item.query.filter_by(project_id=project.id).all()
        
        data = [
            ["رقم البند", "الوصف", "الوحدة", "الكمية التعاقدية", "التكلفة الإفرادية التعاقدية", "التكلفة الإجمالية التعاقدية",
             "الكمية الفعلية", "التكلفة الإفرادية الفعلية", "التكلفة الإجمالية الفعلية", "الحالة",
             "طريقة التنفيذ", "المقاول/المورد", "المبلغ المدفوع", "المبلغ المتبقي", "ملاحظات"]
        ]
        for item in items:
            data.append([
                item.item_number,
                item.description,
                item.unit,
                item.contract_quantity,
                item.contract_unit_cost,
                item.contract_total_cost,
                item.actual_quantity,
                item.actual_unit_cost,
                item.actual_total_cost,
                item.status,
                item.execution_method,
                item.contractor,
                item.paid_amount,
                item.remaining_amount,
                item.notes
            ])
        
        service.write_data("بنود المشروع", data)
        flash("تم تصدير بنود المشروع إلى Google Sheets بنجاح!", "success")
    except Exception as e:
        flash(f"حدث خطأ أثناء تصدير البيانات: {str(e)}", "danger")
    
    return redirect(url_for("project.get_project", project_id=project_id))

@sheets_bp.route("/projects/<int:project_id>/import_contractual", methods=["GET", "POST"])
@login_required
def import_contractual_items(project_id):
    project = Project.query.get_or_404(project_id)
    if not project.spreadsheet_id:
        flash("لا يوجد معرّف Google Sheets لهذا المشروع.", "danger")
        return redirect(url_for("project.get_project", project_id=project_id))

    if request.method == "POST":
        sheet_name = request.form["sheet_name"]
        try:
            service = GoogleSheetsService(project.spreadsheet_id)
            data = service.read_data(sheet_name)
            
            # Assuming first row is header: رقم البند, الوصف, الوحدة, الكمية التعاقدية, التكلفة الإفرادية التعاقدية
            if not data or len(data) < 2:
                flash("لا توجد بيانات كافية في الجدول المحدد.", "warning")
                return redirect(url_for("sheets.import_contractual_items", project_id=project_id))

            headers = [h.strip() for h in data[0]]
            expected_headers = ["رقم البند", "الوصف", "الوحدة", "الكمية التعاقدية", "التكلفة الإفرادية التعاقدية"]
            if not all(h in headers for h in expected_headers):
                flash("تأكد من أن رؤوس الأعمدة في Google Sheet تتطابق مع: رقم البند, الوصف, الوحدة, الكمية التعاقدية, التكلفة الإفرادية التعاقدية", "danger")
                return redirect(url_for("sheets.import_contractual_items", project_id=project_id))

            for row in data[1:]:
                item_data = dict(zip(headers, row))
                
                item_number = item_data.get("رقم البند")
                description = item_data.get("الوصف")
                unit = item_data.get("الوحدة")
                contract_quantity = float(item_data.get("الكمية التعاقدية", 0))
                contract_unit_cost = float(item_data.get("التكلفة الإفرادية التعاقدية", 0))

                if item_number and description:
                    existing_item = Item.query.filter_by(project_id=project.id, item_number=item_number).first()
                    if existing_item:
                        existing_item.description = description
                        existing_item.unit = unit
                        existing_item.contract_quantity = contract_quantity
                        existing_item.contract_unit_cost = contract_unit_cost
                        flash(f"تم تحديث البند {item_number} بنجاح.", "info")
                    else:
                        new_item = Item(project_id=project.id, item_number=item_number, description=description,
                                        unit=unit, contract_quantity=contract_quantity, contract_unit_cost=contract_unit_cost)
                        db.session.add(new_item)
                        flash(f"تم إضافة البند {item_number} بنجاح.", "success")
            db.session.commit()
            flash("تم استيراد البنود التعاقدية بنجاح!", "success")
            return redirect(url_for("project.get_project", project_id=project_id))
        except Exception as e:
            flash(f"حدث خطأ أثناء استيراد البيانات: {str(e)}", "danger")

    return render_template("sheets/import_contractual.html", project=project)

@sheets_bp.route("/projects/<int:project_id>/import_actual", methods=["GET", "POST"])
@login_required
def import_actual_items(project_id):
    project = Project.query.get_or_404(project_id)
    if not project.spreadsheet_id:
        flash("لا يوجد معرّف Google Sheets لهذا المشروع.", "danger")
        return redirect(url_for("project.get_project", project_id=project_id))

    if request.method == "POST":
        sheet_name = request.form["sheet_name"]
        try:
            service = GoogleSheetsService(project.spreadsheet_id)
            data = service.read_data(sheet_name)
            
            # Assuming first row is header: رقم البند, الكمية الفعلية, التكلفة الإفرادية الفعلية, الحالة, المبلغ المدفوع
            if not data or len(data) < 2:
                flash("لا توجد بيانات كافية في الجدول المحدد.", "warning")
                return redirect(url_for("sheets.import_actual_items", project_id=project_id))

            headers = [h.strip() for h in data[0]]
            expected_headers = ["رقم البند", "الكمية الفعلية", "التكلفة الإفرادية الفعلية", "الحالة", "المبلغ المدفوع"]
            if not all(h in headers for h in expected_headers):
                flash("تأكد من أن رؤوس الأعمدة في Google Sheet تتطابق مع: رقم البند, الكمية الفعلية, التكلفة الإفرادية الفعلية, الحالة, المبلغ المدفوع", "danger")
                return redirect(url_for("sheets.import_actual_items", project_id=project_id))

            for row in data[1:]:
                item_data = dict(zip(headers, row))
                
                item_number = item_data.get("رقم البند")
                actual_quantity = float(item_data.get("الكمية الفعلية", 0))
                actual_unit_cost = float(item_data.get("التكلفة الإفرادية الفعلية", 0))
                status = item_data.get("الحالة", "نشط")
                paid_amount = float(item_data.get("المبلغ المدفوع", 0))

                if item_number:
                    existing_item = Item.query.filter_by(project_id=project.id, item_number=item_number).first()
                    if existing_item:
                        existing_item.actual_quantity = actual_quantity
                        existing_item.actual_unit_cost = actual_unit_cost
                        existing_item.status = status
                        existing_item.paid_amount = paid_amount
                        flash(f"تم تحديث البند {item_number} بالبيانات الفعلية بنجاح.", "info")
                    else:
                        flash(f"البند {item_number} غير موجود في المشروع. يرجى إضافته أولاً كبند تعاقدي.", "warning")
            db.session.commit()
            flash("تم استيراد البنود الفعلية بنجاح!", "success")
            return redirect(url_for("project.get_project", project_id=project_id))
        except Exception as e:
            flash(f"حدث خطأ أثناء استيراد البيانات: {str(e)}", "danger")

    return render_template("sheets/import_actual.html", project=project)

@sheets_bp.route("/projects/<int:project_id>/export_summary", methods=["POST"])
@login_required
def export_summary(project_id):
    project = Project.query.get_or_404(project_id)
    if not project.spreadsheet_id:
        flash("لا يوجد معرّف Google Sheets لهذا المشروع.", "danger")
        return redirect(url_for("project.get_project", project_id=project_id))

    try:
        service = GoogleSheetsService(project.spreadsheet_id)
        
        summary_data = [
            ["ملخص المشروع", project.name],
            ["إجمالي التكلفة التعاقدية", project.total_contract_cost],
            ["إجمالي التكلفة الفعلية", project.total_actual_cost],
            ["إجمالي الوفر / الزيادة", project.total_savings],
            ["نسبة إنجاز البنود", f"{project.completion_percentage:.2f}%"],
            ["نسبة الإنجاز المالي", f"{project.financial_completion_percentage:.2f}%"]
        ]
        service.write_data("ملخص المشروع", summary_data)
        flash("تم تصدير ملخص المشروع إلى Google Sheets بنجاح!", "success")
    except Exception as e:
        flash(f"حدث خطأ أثناء تصدير الملخص: {str(e)}", "danger")
    
    return redirect(url_for("project.get_project", project_id=project_id))


>>>>>>> 7a3713e (Initial commit with updated files)
