from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.google_sheets_service import GoogleSheetsService
from app.models.project import Project
from app.models.item import Item
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission # <<< Import the function

sheets_bp = Blueprint("sheets", __name__)

@sheets_bp.route("/projects/<int:project_id>/export_items", methods=["POST"])
@login_required
def export_project(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project) # <<< Add permission check
    if not project.spreadsheet_id:
        flash("لا يوجد معرّف Google Sheets لهذا المشروع.", "danger")
        return redirect(url_for("project.get_project", project_id=project_id))
    # ... (rest of the function is the same)
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
    check_project_permission(project) # <<< Add permission check
    if not project.spreadsheet_id:
        flash("لا يوجد معرّف Google Sheets لهذا المشروع.", "danger")
        return redirect(url_for("project.get_project", project_id=project_id))
    # ... (rest of the function is the same)
    if request.method == "POST":
        sheet_name = request.form["sheet_name"]
        try:
            service = GoogleSheetsService(project.spreadsheet_id)
            data = service.read_data(sheet_name)
            
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
    check_project_permission(project) # <<< Add permission check
    if not project.spreadsheet_id:
        flash("لا يوجد معرّف Google Sheets لهذا المشروع.", "danger")
        return redirect(url_for("project.get_project", project_id=project_id))
    # ... (rest of the function is the same)
    if request.method == "POST":
        sheet_name = request.form["sheet_name"]
        try:
            service = GoogleSheetsService(project.spreadsheet_id)
            data = service.read_data(sheet_name)
            
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