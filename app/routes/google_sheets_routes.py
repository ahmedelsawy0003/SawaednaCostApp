from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.google_sheets_service import GoogleSheetsService
from app.models.project import Project
from app.models.item import Item
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission

sheets_bp = Blueprint("sheets", __name__)

@sheets_bp.route("/projects/<int:project_id>/export_items", methods=["POST"])
@login_required
def export_project(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
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
    check_project_permission(project)
    if not project.spreadsheet_id:
        flash("لا يوجد معرّف Google Sheets لهذا المشروع.", "danger")
        return redirect(url_for("project.get_project", project_id=project_id))
    
    if request.method == "POST":
        sheet_name = request.form["sheet_name"]
        try:
            service = GoogleSheetsService(project.spreadsheet_id)
            data = service.read_data(sheet_name)
            
            if not data or len(data) < 2:
                flash("لا توجد بيانات كافية في الجدول المحدد.", "warning")
                return redirect(url_for("sheets.import_contractual_items", project_id=project_id))

            headers = [h.strip() for h in data[0]]
            
            # START: Smart column detection
            # Define possible names for each column to handle variations
            col_map = {
                'item_number': ['رقم البند'],
                'item_name': ['اسم البند'],
                'description': ['الوصف', 'وصف البند'],
                'unit': ['الوحدة'],
                'quantity': ['الكمية', 'الكمية التعاقدية'],
                'unit_cost': ['السعر الافرادى التعاقدي', 'التكلفة الإفرادية التعاقدية']
            }

            # Find the actual index of each column based on possible names
            header_indices = {}
            for key, possible_names in col_map.items():
                for name in possible_names:
                    if name in headers:
                        header_indices[key] = headers.index(name)
                        break
            
            required_keys = ['item_number', 'description', 'unit', 'quantity', 'unit_cost']
            if not all(key in header_indices for key in required_keys):
                flash(f"لم يتم العثور على كل الأعمدة المطلوبة. يرجى التأكد من وجود: {', '.join(required_keys)}", "danger")
                return redirect(url_for("sheets.import_contractual_items", project_id=project_id))
            # END: Smart column detection

            for row in data[1:]:
                # Ensure row has enough columns
                if not any(row): continue # Skip empty rows

                item_number = row[header_indices['item_number']].strip()
                
                # Combine 'item_name' and 'description' if both exist
                item_desc = row[header_indices['description']].strip()
                if 'item_name' in header_indices and header_indices['item_name'] < len(row):
                    item_name = row[header_indices['item_name']].strip()
                    if item_name:
                        item_desc = f"{item_name} - {item_desc}"

                unit = row[header_indices['unit']].strip()
                quantity = float(row[header_indices['quantity']].strip() or 0)
                unit_cost = float(row[header_indices['unit_cost']].strip() or 0)

                if item_number:
                    existing_item = Item.query.filter_by(project_id=project.id, item_number=item_number).first()
                    if existing_item:
                        existing_item.description = item_desc
                        existing_item.unit = unit
                        existing_item.contract_quantity = quantity
                        existing_item.contract_unit_cost = unit_cost
                    else:
                        new_item = Item(
                            project_id=project.id, 
                            item_number=item_number, 
                            description=item_desc,
                            unit=unit, 
                            contract_quantity=quantity, 
                            contract_unit_cost=unit_cost
                        )
                        db.session.add(new_item)
            
            db.session.commit()
            flash("تم استيراد البنود التعاقدية بنجاح!", "success")
            return redirect(url_for("project.get_project", project_id=project_id))
        except Exception as e:
            db.session.rollback()
            flash(f"حدث خطأ أثناء استيراد البيانات: {str(e)}", "danger")

    return render_template("sheets/import_contractual.html", project=project)


@sheets_bp.route("/projects/<int:project_id>/import_actual", methods=["GET", "POST"])
@login_required
def import_actual_items(project_id):
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    if not project.spreadsheet_id:
        flash("لا يوجد معرّف Google Sheets لهذا المشروع.", "danger")
        return redirect(url_for("project.get_project", project_id=project_id))
    
    if request.method == "POST":
        sheet_name = request.form["sheet_name"]
        try:
            service = GoogleSheetsService(project.spreadsheet_id)
            data = service.read_data(sheet_name)
            
            if not data or len(data) < 2:
                flash("لا توجد بيانات كافية في الجدول المحدد.", "warning")
                return redirect(url_for("sheets.import_actual_items", project_id=project_id))

            headers = [h.strip() for h in data[0]]
            expected_headers = ["رقم البند", "الكمية الفعلية", "التكلفة الإفرادية الفعلية", "الحالة"]
            if not all(h in headers for h in expected_headers):
                flash("تأكد من أن رؤوس الأعمدة في Google Sheet تتطابق مع: رقم البند, الكمية الفعلية, التكلفة الإفرادية الفعلية, الحالة", "danger")
                return redirect(url_for("sheets.import_actual_items", project_id=project_id))

            for row in data[1:]:
                item_data = dict(zip(headers, row))
                
                item_number = item_data.get("رقم البند")
                actual_quantity = float(item_data.get("الكمية الفعلية", 0))
                actual_unit_cost = float(item_data.get("التكلفة الإفرادية الفعلية", 0))
                status = item_data.get("الحالة", "نشط")

                if item_number:
                    existing_item = Item.query.filter_by(project_id=project.id, item_number=item_number).first()
                    if existing_item:
                        existing_item.actual_quantity = actual_quantity
                        existing_item.actual_unit_cost = actual_unit_cost
                        existing_item.status = status
                    else:
                        flash(f"البند {item_number} غير موجود في المشروع. يرجى إضافته أولاً كبند تعاقدي.", "warning")
            
            db.session.commit()
            flash("تم استيراد البنود الفعلية بنجاح!", "success")
            return redirect(url_for("project.get_project", project_id=project_id))
        except Exception as e:
            db.session.rollback()
            flash(f"حدث خطأ أثناء استيراد البيانات: {str(e)}", "danger")

    return render_template("sheets/import_actual.html", project=project)