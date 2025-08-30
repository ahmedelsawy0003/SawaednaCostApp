from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_

from app.models.contractor import Contractor
from app.models.item import Item
from app.models.cost_detail import CostDetail
from app.models.project import Project

api_bp = Blueprint("api", __name__, url_prefix='/api')

@api_bp.route("/contractors/<int:contractor_id>/projects")
@login_required
def get_projects_for_contractor(contractor_id):
    """
    API: يجلب المشاريع المرتبطة بمقاول معين.
    """
    # ابحث عن كل البنود المرتبطة بالمقاول
    items_query = Item.query.filter(
        or_(
            Item.contractor_id == contractor_id,
            Item.cost_details.any(CostDetail.contractor_id == contractor_id)
        )
    )
    
    # فلترة حسب صلاحيات المستخدم
    if current_user.role != 'admin':
        allowed_project_ids = [p.id for p in current_user.projects]
        items_query = items_query.filter(Item.project_id.in_(allowed_project_ids))

    # استخراج المشاريع الفريدة من البنود
    project_ids = {item.project_id for item in items_query.all()}
    projects = Project.query.filter(Project.id.in_(project_ids)).order_by(Project.name).all()
    
    return jsonify([{'id': p.id, 'name': p.name} for p in projects])


@api_bp.route("/projects/<int:project_id>/contractors/<int:contractor_id>/items")
@login_required
def get_items_for_project_contractor(project_id, contractor_id):
    """
    API: يجلب البنود المرتبطة بمشروع ومقاول معينين.
    """
    subquery = Item.id.in_(db.session.query(Item.id).join(CostDetail).filter(CostDetail.contractor_id == contractor_id))
    items_query = Item.query.filter(
        Item.project_id == project_id,
        or_(
            Item.contractor_id == contractor_id,
            subquery
        )
    ).order_by(Item.item_number)
    
    items = items_query.all()
    return jsonify([{'id': item.id, 'name': f"{item.item_number} - {item.short_description}"} for item in items])


@api_bp.route("/items/<int:item_id>/contractors/<int:contractor_id>/cost_details")
@login_required
def get_cost_details_for_item_contractor(item_id, contractor_id):
    """
    API: يجلب تفاصيل التكاليف غير المدفوعة لبند ومقاول معين.
    """
    cost_details = CostDetail.query.filter(
        CostDetail.item_id == item_id,
        or_(
            CostDetail.contractor_id == contractor_id,
            # Handle case where item is assigned to contractor but detail is self-executed
            (CostDetail.contractor_id == None) & (CostDetail.item.has(Item.contractor_id == contractor_id))
        )
    ).all()
    
    # فلترة التفاصيل التي لم يتم دفعها بالكامل فقط
    unpaid_details = [cd for cd in cost_details if cd.payment_status != 'مدفوع بالكامل']
    
    return jsonify([{
        'id': detail.id, 
        'name': f"{detail.description} (المتبقي: {detail.remaining_amount:,.2f} ريال)"
    } for detail in unpaid_details])