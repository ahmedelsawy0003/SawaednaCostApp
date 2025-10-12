from flask import Blueprint, render_template, request, url_for
from app.models.cost_detail import CostDetail
from app.models.invoice import Invoice
from app.models.item import Item
from app.models.project import Project
from app.models.contractor import Contractor
from flask_login import login_required, current_user
from sqlalchemy import or_

po_bp = Blueprint("po", __name__, url_prefix='/purchase_orders')

@po_bp.route("/")
@login_required
def get_all_purchase_orders():
    """
    يعرض قائمة شاملة بجميع أوامر الشراء المسجلة (من تفاصيل التكاليف أو المستخلصات).
    """
    
    # 1. استعلام تفاصيل التكلفة التي تحتوي على رقم أمر شراء
    cost_detail_query = CostDetail.query.filter(
        CostDetail.purchase_order_number.isnot(None),
        CostDetail.purchase_order_number != ''
    )

    # 2. استعلام المستخلصات/الفواتير التي تحتوي على رقم أمر شراء
    invoice_query = Invoice.query.filter(
        Invoice.purchase_order_number.isnot(None),
        Invoice.purchase_order_number != ''
    )
    
    # تطبيق فلاتر الصلاحيات للمستخدم العادي
    if current_user.role not in ['admin', 'sub-admin']:
        allowed_project_ids = [p.id for p in current_user.projects]
        if not allowed_project_ids:
            # يجب أن يكون هذا مسارًا جديدًا يجب إنشاؤه
            return render_template("purchase_orders/index.html", records=[], projects=[], filters={})

        cost_detail_query = cost_detail_query.join(CostDetail.item).filter(
            Item.project_id.in_(allowed_project_ids)
        )
        invoice_query = invoice_query.filter(
            Invoice.project_id.in_(allowed_project_ids)
        )

    # تطبيق فلاتر البحث
    search_term = request.args.get('search', '').strip()
    project_id = request.args.get('project_id', type=int)
    
    if search_term:
        search_like = f"%{search_term}%"
        
        cost_detail_query = cost_detail_query.join(CostDetail.contractor, isouter=True).filter(
            or_(
                CostDetail.purchase_order_number.ilike(search_like),
                CostDetail.description.ilike(search_like),
                Contractor.name.ilike(search_like)
            )
        )
        
        invoice_query = invoice_query.join(Contractor).filter(
            or_(
                Invoice.purchase_order_number.ilike(search_like),
                Contractor.name.ilike(search_like)
            )
        )
    
    if project_id:
        cost_detail_query = cost_detail_query.join(CostDetail.item).filter(
            Item.project_id == project_id
        )
        invoice_query = invoice_query.filter(
            Invoice.project_id == project_id
        )

    # جلب ودمج النتائج
    cost_details = cost_detail_query.order_by(CostDetail.id.desc()).all()
    invoices = invoice_query.order_by(Invoice.id.desc()).all()

    records = []

    for detail in cost_details:
        records.append({
            'type': 'CostDetail',
            'id': detail.id,
            'po_number': detail.purchase_order_number,
            'project_name': detail.item.project.name,
            'contractor_name': detail.contractor.name if detail.contractor else 'شراء مباشر',
            'description': detail.description,
            'amount': detail.total_cost,
            'link': url_for('item.edit_item', item_id=detail.item_id)
        })

    for invoice in invoices:
        records.append({
            'type': 'Invoice',
            'id': invoice.id,
            'po_number': invoice.purchase_order_number,
            'project_name': invoice.project.name,
            'contractor_name': invoice.contractor.name,
            'description': f"مستخلص/فاتورة: {invoice.invoice_number}",
            'amount': invoice.total_amount,
            'link': url_for('invoice.show_invoice', invoice_id=invoice.id)
        })

    # فرز النتائج المدمجة (حسب رقم أمر الشراء)
    records.sort(key=lambda x: x['po_number'], reverse=True)

    # جلب المشاريع لقائمة الفلتر
    projects_for_filter = Project.query.order_by(Project.name).all()
    
    filters = {
        'search': search_term,
        'project_id': project_id
    }
    
    return render_template(
        "purchase_orders/index.html",
        records=records,
        projects=projects_for_filter,
        filters=filters
    )