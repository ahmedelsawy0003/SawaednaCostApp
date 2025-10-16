from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from app.models.contractor import Contractor
from app.models.project import Project
# from app.models.user import User # <<< تم الحذف (غير مستخدمة في المنطق الحالي)
from app.models.invoice import Invoice
from app.models.item import Item 
from app.extensions import db
from flask_login import login_required, current_user
# from sqlalchemy import or_ # <<< تم الحذف (غير مستخدمة في المنطق الحالي)
from app.utils import sanitize_input
from app.forms import ContractorForm 

contractor_bp = Blueprint("contractor", __name__, url_prefix='/contractors')

@contractor_bp.route("/")
@login_required
def get_contractors():
    """عرض قائمة بجميع المقاولين"""
    # --- START: التعديل الرئيسي هنا ---
    if current_user.role not in ['admin', 'sub-admin']:
    # --- END: التعديل الرئيسي هنا ---
        allowed_project_ids = [p.id for p in current_user.projects]
        if not allowed_project_ids:
            contractors = []
        else:
            # يجب السماح بعرض المقاولين المرتبطين بالبنود أيضاً، لذا يجب إضافة join إلى Item أيضاً
            contractors_from_invoices = Contractor.query.join(Invoice).join(Project).filter(
                Project.id.in_(allowed_project_ids)
            )
            contractors_from_items = Contractor.query.join(Item).join(Project).filter(
                Project.id.in_(allowed_project_ids)
            )
            
            # دمج النتائج وفرزها
            contractors = contractors_from_invoices.union(contractors_from_items).distinct().order_by(Contractor.name).all()
    else:
        contractors = Contractor.query.order_by(Contractor.name).all()
    
    return render_template("contractors/index.html", contractors=contractors)

@contractor_bp.route("/new", methods=['GET', 'POST'])
@login_required
def new_contractor():
    if current_user.role not in ['admin', 'sub-admin']:
        abort(403)
    
    form = ContractorForm() 
    
    if form.validate_on_submit():
        new_contractor = Contractor(
            name=form.name.data,
            contact_person=form.contact_person.data,
            phone=form.phone.data,
            email=form.email.data,
            notes=form.notes.data
        )
        db.session.add(new_contractor)
        db.session.commit()
        # UX IMPROVEMENT: Clearer success message
        flash(f'تمت إضافة المقاول "{new_contractor.name}" بنجاح! يمكن الآن إسناد البنود والمستخلصات إليه.', 'success')
        return redirect(url_for('contractor.get_contractors'))
    
    return render_template("contractors/new.html", form=form)

@contractor_bp.route("/<int:contractor_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_contractor(contractor_id):
    if current_user.role not in ['admin', 'sub-admin']:
        abort(403)
    
    contractor = Contractor.query.get_or_404(contractor_id)
    form = ContractorForm(obj=contractor, original_name=contractor.name)
    
    if form.validate_on_submit():
        form.populate_obj(contractor)
        db.session.commit()
        # UX IMPROVEMENT: Clearer success message
        flash(f'تم تحديث بيانات المقاول "{contractor.name}" بنجاح!', 'success')
        return redirect(url_for('contractor.get_contractors'))

    return render_template("contractors/edit.html", form=form, contractor=contractor)


@contractor_bp.route("/<int:contractor_id>/delete", methods=['POST'])
@login_required
def delete_contractor(contractor_id):
    if current_user.role not in ['admin', 'sub-admin']:
        abort(403)
        
    contractor = Contractor.query.get_or_404(contractor_id)
    
    # Check for linked invoices or items
    if contractor.invoices.count() > 0 or contractor.items.count() > 0 or contractor.cost_details.count() > 0:
        # UX IMPROVEMENT: Clearer error message specifying the reason
        flash('لا يمكن حذف هذا المقاول لوجود مستخلصات، أو بنود، أو تفاصيل تكلفة مرتبطة به. يرجى حذف الارتباطات أولاً.', 'danger')
        return redirect(url_for('contractor.show_contractor', contractor_id=contractor_id))
        
    db.session.delete(contractor)
    db.session.commit()
    # UX IMPROVEMENT: Clearer success message
    flash(f"تم حذف المقاول '{contractor.name}' وكل ما يتعلق به بنجاح.", "success")
    return redirect(url_for('contractor.get_contractors'))

@contractor_bp.route("/<int:contractor_id>")
@login_required
def show_contractor(contractor_id):
    contractor = Contractor.query.get_or_404(contractor_id)
    
    invoices_query = Invoice.query.filter_by(contractor_id=contractor_id)
    project_filter = request.args.get('project_id', type=int)
    search_filter = request.args.get('search', '')

    if project_filter:
        invoices_query = invoices_query.filter(Invoice.project_id == project_filter)
    if search_filter:
        search_term = f"%{search_filter}%"
        invoices_query = invoices_query.filter(Invoice.invoice_number.ilike(search_term))
    
    invoices = invoices_query.order_by(Invoice.invoice_date.desc()).all()
    
    total_due = sum(inv.total_amount for inv in invoices if inv.status != 'ملغي')
    total_paid = sum(inv.paid_amount for inv in invoices if inv.status != 'ملغي')
    remaining = total_due - total_paid

    
    # 1. Projects linked via Invoices
    projects_via_invoices = Project.query.join(Invoice).filter(Invoice.contractor_id == contractor_id)
    
    # 2. Projects linked via Items (Contractor assigned to the item)
    projects_via_items = Project.query.join(Item).filter(Item.contractor_id == contractor_id)

    # 3. Combine and apply user permission filter
    projects_query = projects_via_invoices.union(projects_via_items)

    if current_user.role not in ['admin', 'sub-admin']:
        # Filter combined projects by user access
        from app.models.user import User # <<< استيراد محلي للحاجة فقط
        projects_query = projects_query.join(Project.users).filter(User.id == current_user.id)
    
    projects = projects_query.distinct().order_by(Project.name).all()

    assigned_items = Item.query.filter_by(contractor_id=contractor_id).order_by(Item.project_id, Item.item_number).all()

    return render_template(
        "contractors/show.html", 
        contractor=contractor, 
        invoices=invoices,
        projects=projects,
        assigned_items=assigned_items, 
        total_due=total_due,
        total_paid=total_paid,
        remaining=remaining,
        filters={'project_id': project_filter, 'search': search_filter}
    )