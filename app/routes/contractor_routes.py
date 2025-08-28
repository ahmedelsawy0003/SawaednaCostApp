from flask import Blueprint, render_template, request, abort
from app.models.contractor import Contractor
from app.models.cost_detail import CostDetail
from app.models.project import Project
from app.extensions import db
from flask_login import login_required, current_user
from sqlalchemy import or_

contractor_bp = Blueprint("contractor", __name__, url_prefix='/contractors')

@contractor_bp.route("/")
@login_required
def get_contractors():
    """عرض قائمة بجميع المقاولين"""
    # سيتم عرض جميع المقاولين للمسؤول, والمقاولين المرتبطين بمشاريع المستخدم فقط للمستخدم العادي
    query = Contractor.query.join(CostDetail).join(CostDetail.item)

    if current_user.role != 'admin':
        # فلترة المقاولين بناءً على المشاريع المسموح للمستخدم بالوصول إليها
        allowed_project_ids = [p.id for p in current_user.projects]
        query = query.filter(CostDetail.item.has(project_id.in_(allowed_project_ids)))

    contractors = query.distinct().order_by(Contractor.name).all()
    
    return render_template("contractors/index.html", contractors=contractors)

@contractor_bp.route("/<int:contractor_id>")
@login_required
def show_contractor(contractor_id):
    """عرض صفحة تفصيلية للمقاول مع جميع تفاصيل التكاليف والدفعات المرتبطة به"""
    contractor = Contractor.query.get_or_404(contractor_id)

    # فلترة المشاريع للdropdown
    projects_query = Project.query.join(Project.items).join(Item.cost_details).filter(CostDetail.contractor_id == contractor_id)
    if current_user.role != 'admin':
        projects_query = projects_query.join(Project.users).filter(User.id == current_user.id)
    
    projects = projects_query.distinct().all()

    # جلب فلاتر البحث من الـ URL
    project_filter = request.args.get('project_id', type=int)
    search_filter = request.args.get('search', '')

    # بناء الاستعلام الأساسي لتفاصيل التكاليف
    cost_details_query = CostDetail.query.filter_by(contractor_id=contractor_id)

    # تطبيق الفلاتر
    if project_filter:
        cost_details_query = cost_details_query.join(CostDetail.item).filter_by(project_id=project_filter)
    
    if search_filter:
        search_term = f"%{search_filter}%"
        cost_details_query = cost_details_query.filter(
            or_(
                CostDetail.description.ilike(search_term),
                CostDetail.item.has(Item.item_number.ilike(search_term))
            )
        )
    
    cost_details = cost_details_query.all()
    
    # حساب الإحصائيات
    total_due = sum(cd.total_cost for cd in cost_details)
    total_paid = sum(cd.total_paid for cd in cost_details)
    remaining = total_due - total_paid

    return render_template(
        "contractors/show.html", 
        contractor=contractor, 
        cost_details=cost_details,
        projects=projects,
        total_due=total_due,
        total_paid=total_paid,
        remaining=remaining,
        filters={'project_id': project_filter, 'search': search_filter}
    )