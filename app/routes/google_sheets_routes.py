from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.services.google_sheets_service import GoogleSheetsService
from app.models.project import Project
from app.models.item import Item
from app.extensions import db
from flask_login import login_required, current_user
from app.utils import check_project_permission, sanitize_input

sheets_bp = Blueprint("sheets", __name__)

@sheets_bp.route("/projects/<int:project_id>/export_items", methods=["POST"])
@login_required
def export_project(project_id):
    if current_user.role not in ['admin', 'sub-admin']:
        abort(403)
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    if not project.spreadsheet_id:
        # UX IMPROVEMENT: Clearer guiding message
        flash("فشل التصدير: لا يوجد معرّف Google Sheets مرتبط بهذا المشروع. يرجى تعديل المشروع وربطه بالملف.", "danger")
        return redirect(url_for("project.get_project", project_id=project_id))
    
    try:
        service = GoogleSheetsService(project.spreadsheet_id)
        items = Item.query.filter_by(project_id=project.id).order_by(Item.item_number).all()
        
        data = []
        headers = [
            "رقم البند", "الوصف", "الوحدة", "الكمية التعاقدية", 
            "التكلفة الإفرادية التعاقدية", "التكلفة الإجمالية التعاقدية",
            "الكمية الفعلية", "التكلفة الإفرادية الفعلية", "التكلفة الإجمالية الفعلية", 
            "الحالة", "المقاول/المورد", "المبلغ المدفوع", "المبلغ المتبقي", "ملاحظات"
        ]
        data.append(headers)

        for item in items:
            data.append([
                item.item_number, item.description, item.unit,
                item.contract_quantity, item.contract_unit_cost, item.contract_total_cost,
                # NOTE: The following two fields are deprecated in the new model structure, but kept for compatibility or manual input reference
                item.actual_quantity, item.actual_unit_cost, item.actual_total_cost, 
                item.status,
                item.contractor.name if item.contractor else "",
                item.paid_amount, item.remaining_amount, item.notes
            ])
        
        success, error_message = service.write_data("تفاصيل بنود المشروع", data)
        if success:
            flash("تم تصدير جميع بنود المشروع إلى ورقة عمل جديدة في Google Sheets بنجاح!", "success")
        else:
            # UX IMPROVEMENT: Clearer error message for service failure
            flash(f"حدث خطأ أثناء التصدير إلى Google Sheets: {error_message}. يرجى مراجعة إعدادات الصلاحية.", "danger")

    except Exception as e:
        # UX IMPROVEMENT: Clearer unexpected error message
        flash(f"حدث خطأ غير متوقع أثناء التصدير: {str(e)}. يرجى التأكد من صحة معرّف Sheets.", "danger")
    
    return redirect(url_for("project.get_project", project_id=project_id))

@sheets_bp.route("/projects/<int:project_id>/export_summary", methods=["POST"])
@login_required
def export_summary(project_id):
    if current_user.role not in ['admin', 'sub-admin']:
        abort(403)
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    if not project.spreadsheet_id:
        # UX IMPROVEMENT: Clearer guiding message
        flash("فشل التصدير: لا يوجد معرّف Google Sheets مرتبط بهذا المشروع. يرجى تعديل المشروع وربطه بالملف.", "danger")
        return redirect(url_for("project.get_project", project_id=project_id))

    try:
        service = GoogleSheetsService(project.spreadsheet_id)
        
        # Recalculate dashboard metrics needed for the summary
        if not project.items:
            completion_percentage = 0.0
        else:
            completed_items = sum(1 for item in project.items if item.status == 'مكتمل')
            completion_percentage = (completed_items / len(project.items)) * 100 if project.items else 0.0

        if project.total_actual_cost == 0:
            financial_completion_percentage = 0.0
        else:
            financial_completion_percentage = (project.total_paid_amount / project.total_actual_cost) * 100

        summary_data = [
            ["ملخص المشروع: " + project.name, ""],
            ["الحقل", "القيمة"],
            ["إجمالي التكلفة التعاقدية", project.total_contract_cost],
            ["إجمالي الوفر / الزيادة", project.total_savings],
            ["إجمالي التكلفة الفعلية", project.total_actual_cost],
            ["إجمالي المبلغ المدفوع", project.total_paid_amount],
            ["إجمالي المبلغ المتبقي", project.total_remaining_amount],
            [f"نسبة إنجاز البنود (كمي)", f"{completion_percentage:.2f}%"],
            [f"نسبة الإنجاز المالي", f"{financial_completion_percentage:.2f}%"]
        ]

        success, error_message = service.write_data("ملخص المشروع", summary_data)
        if success:
            flash("تم تصدير الملخص المالي للمشروع إلى ورقة عمل جديدة بنجاح!", "success")
        else:
            # UX IMPROVEMENT: Clearer error message for service failure
            flash(f"حدث خطأ أثناء التصدير إلى Google Sheets: {error_message}. يرجى مراجعة إعدادات الصلاحية.", "danger")

    except Exception as e:
        # UX IMPROVEMENT: Clearer unexpected error message
        flash(f"حدث خطأ غير متوقع أثناء التصدير: {str(e)}. يرجى التأكد من صحة معرّف Sheets.", "danger")

    return redirect(url_for("project.get_project", project_id=project_id))


# --- START: التعديل الشامل لدالة الاستيراد مع جلب أسماء الشيتات ---
@sheets_bp.route("/projects/<int:project_id>/import_items", methods=["GET", "POST"])
@login_required
def import_items(project_id):
    if current_user.role not in ['admin', 'sub-admin']:
        abort(403)
    
    project = Project.query.get_or_404(project_id)
    check_project_permission(project)
    if not project.spreadsheet_id:
        # UX IMPROVEMENT: Clearer guiding message
        flash("فشل الاستيراد: لا يوجد معرّف Google Sheets مرتبط بهذا المشروع. يرجى تعديل المشروع وربطه بالملف.", "danger")
        return redirect(url_for("project.get_project", project_id=project_id))
    
    # جلب أسماء الشيتات في كل الأحوال (GET and POST) لعرضها في حال حدوث خطأ
    sheet_names = None
    try:
        service = GoogleSheetsService(project.spreadsheet_id)
        sheet_names_list, error = service.get_sheet_names()
        if error:
            # UX IMPROVEMENT: Clearer error message for connection
            flash(f"خطأ في الاتصال بملف Google Sheets: {error}. يرجى التحقق من صحة المعرّف (ID) وصلاحيات الوصول.", "danger")
            # If error, sheet_names_list is None, so check for that below
            sheet_names = []
        else:
            sheet_names = sheet_names_list
    except Exception as e:
        # UX IMPROVEMENT: Clearer unexpected error message
        flash(f"حدث خطأ غير متوقع أثناء محاولة قراءة الملف: {str(e)}", "danger")
        return redirect(url_for('project.get_project', project_id=project_id))
    
    if request.method == "POST":
        sheet_name = request.form.get("sheet_name") # استخدام .get لتجنب الخطأ إذا لم يتم اختيار شيء
        if not sheet_name:
            flash("الرجاء اختيار ورقة عمل (شيت) للاستيراد منها.", "warning")
            return render_template("sheets/import_contractual.html", project=project, sheet_names=sheet_names)

        try:
            data = service.read_data(sheet_name)
            
            if not data or len(data) < 2:
                flash(f"لا توجد بيانات كافية في ورقة العمل '{sheet_name}'. تأكد من وجود صفوف بيانات بعد العناوين.", "warning")
                return redirect(url_for("sheets.import_items", project_id=project_id))

            # Logic to process and map data... (This part remains the same logic as the original implementation)
            headers = [h.strip().replace('ى', 'ي').replace('ه', 'ة') for h in data[0]]
            
            col_map = {
                'item_number': ['رقم البند', 'الرقم التسلسلي', 'الرقم', 'رقم', 'مسلسل'],
                'item_name': ['اسم البند'],
                'description': ['الوصف', 'وصف البند', 'البيان'],
                'unit': ['الوحدة', 'وحدة القياس'],
                'quantity': ['الكمية', 'الكمية التعاقدية'],
                'unit_cost': ['السعر الافرادى التعاقدي', 'التكلفة الإفرادية التعاقدية', 'السعر', 'السعر التعاقدي', 'التكلفة', 'التكلفة التعاقدية', 'تكلفة', 'سعر', 'سعر افرادى']
            }

            header_indices = {}
            for key, possible_names in col_map.items():
                normalized_possible_names = [name.replace('ى', 'ي').replace('ه', 'ة') for name in possible_names]
                for name in normalized_possible_names:
                    if name in headers:
                        header_indices[key] = headers.index(name)
                        break
            
            required_keys = ['item_number', 'description', 'unit', 'quantity', 'unit_cost']
            missing_keys = [key for key in required_keys if key not in header_indices]
            
            if missing_keys:
                # UX IMPROVEMENT: Clearer error message for missing columns
                missing_names = [name for key in missing_keys for name in col_map[key] if name in headers or name is not None]
                flash(f"لم يتم العثور على الأعمدة الإلزامية المطلوبة. يرجى التأكد من وجود أعمدة تعبر عن: {', '.join([col_map[k][0] for k in missing_keys])}.", "danger")
                return redirect(url_for("sheets.import_items", project_id=project_id))

            updated_count = 0
            new_count = 0
            for row_idx, row in enumerate(data[1:], start=2):
                if not any(row): continue
                try:
                    # Sanitize inputs from external sheet
                    item_number = sanitize_input(row[header_indices['item_number']].strip())
                    item_desc = sanitize_input(row[header_indices['description']].strip())
                    unit = sanitize_input(row[header_indices['unit']].strip())
                    quantity_str = row[header_indices['quantity']].strip().replace(',', '')
                    unit_cost_str = row[header_indices['unit_cost']].strip().replace(',', '')

                    if 'item_name' in header_indices and header_indices['item_name'] < len(row):
                        item_name = sanitize_input(row[header_indices['item_name']].strip())
                        if item_name:
                            item_desc = f"{item_name} - {item_desc}"
                        
                    # Handle empty strings to float conversion
                    contract_quantity = float(quantity_str) if quantity_str else 0.0
                    contract_unit_cost = float(unit_cost_str) if unit_cost_str else 0.0
                    
                    if contract_quantity <= 0 or contract_unit_cost <= 0:
                        # Skip if essential values are zero or missing, log a warning instead of aborting
                        flash(f"تم تخطي الصف رقم {row_idx}: الكمية أو السعر التعاقدي يساوي صفر.", "warning")
                        continue

                    # Default actual values based on contract
                    actual_quantity = contract_quantity
                    actual_unit_cost = contract_unit_cost * 0.70 # Default 70%

                    if item_number:
                        existing_item = Item.query.filter_by(project_id=project.id, item_number=item_number).first()
                        if existing_item:
                            existing_item.description = item_desc
                            existing_item.unit = unit
                            existing_item.contract_quantity = contract_quantity
                            existing_item.contract_unit_cost = contract_unit_cost
                            existing_item.actual_quantity = actual_quantity
                            existing_item.actual_unit_cost = actual_unit_cost
                            updated_count += 1
                        else:
                            new_item = Item(
                                project_id=project.id, item_number=item_number, description=item_desc,
                                unit=unit, contract_quantity=contract_quantity, contract_unit_cost=contract_unit_cost,
                                actual_quantity=actual_quantity, actual_unit_cost=actual_unit_cost
                            )
                            db.session.add(new_item)
                            new_count += 1
                except (ValueError, IndexError) as e:
                    # UX IMPROVEMENT: Clearer error message
                    flash(f"خطأ في بيانات الصف رقم {row_idx}: {e}. يرجى مراجعة قيم الكمية والسعر.", "danger")
            
            db.session.commit()
            # UX IMPROVEMENT: Clear and informative summary message
            flash(f"تمت عملية الاستيراد بنجاح! ({new_count} بنود جديدة مضافة و {updated_count} بند محدث).", "success")
            return redirect(url_for("project.get_project", project_id=project_id))
        except Exception as e:
            db.session.rollback()
            # UX IMPROVEMENT: Clearer unexpected error message
            flash(f"حدث خطأ أثناء معالجة بيانات ورقة العمل: {str(e)}. يرجى مراجعة تنسيق البيانات (الأرقام).", "danger")

    return render_template("sheets/import_contractual.html", project=project, sheet_names=sheet_names)
# --- END: التعديل الشامل ---