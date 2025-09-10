from flask import Blueprint, render_template, request, jsonify, abort
from app.models.payment import Payment
from app.models.project import Project
from app.models.contractor import Contractor
from app.models.invoice import Invoice
from app.models.payment_distribution import PaymentDistribution
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from app.extensions import db
import datetime
from app.utils import check_project_permission

payment_bp = Blueprint("payment", __name__, url_prefix='/payments')

@payment_bp.route("/")
@login_required
def get_all_payments():
    """
    يعرض صفحة شاملة لجميع الدفعات مع فلاتر بحث متقدمة.
    """
    query = Payment.query.join(Invoice).join(Contractor)

    # تطبيق الفلاتر بناءً على صلاحيات المستخدم
    if current_user.role not in ['admin', 'sub-admin']:
        allowed_project_ids = [p.id for p in current_user.projects]
        query = query.filter(Invoice.project_id.in_(allowed_project_ids))

    # قراءة الفلاتر من الرابط
    search_term = request.args.get('search', '')
    project_id = request.args.get('project_id', type=int)
    contractor_id = request.args.get('contractor_id', type=int)
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')

    # تطبيق الفلاتر على الاستعلام
    if search_term:
        query = query.filter(
            or_(
                Payment.description.ilike(f"%{search_term}%"),
                Invoice.invoice_number.ilike(f"%{search_term}%"),
                Contractor.name.ilike(f"%{search_term}%")
            )
        )
    if project_id:
        query = query.filter(Invoice.project_id == project_id)
    if contractor_id:
        query = query.filter(Invoice.contractor_id == contractor_id)
    if start_date_str:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        query = query.filter(Payment.payment_date >= start_date)
    if end_date_str:
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        query = query.filter(Payment.payment_date <= end_date)

    payments = query.order_by(Payment.payment_date.desc()).options(
        joinedload(Payment.distributions).joinedload(PaymentDistribution.invoice_item)
    ).all()
    
    # Prepare JSON-serializable distributions for template
    payments_distributions = {}
    for payment in payments:
        dists = []
        for dist in payment.distributions:
            description = dist.invoice_item.description if dist.invoice_item else ''
            dists.append({
                'description': description,
                'amount': dist.amount
            })
        # attach transient attribute for template consumption
        payment.distributions_json = dists
        payments_distributions[payment.id] = dists
    
    # جلب المشاريع والمقاولين لقوائم الفلترة
    projects = Project.query.order_by(Project.name).all()
    contractors = Contractor.query.order_by(Contractor.name).all()

    filters = {
        'search': search_term,
        'project_id': project_id,
        'contractor_id': contractor_id,
        'start_date': start_date_str,
        'end_date': end_date_str
    }
    
    return render_template(
        "payments/index.html",
        payments=payments,
        projects=projects,
        contractors=contractors,
        filters=filters,
        payments_distributions=payments_distributions
    )


@payment_bp.route("/<int:payment_id>/distributions.json")
@login_required
def get_payment_distributions(payment_id):
    payment = Payment.query.options(
        joinedload(Payment.distributions).joinedload(PaymentDistribution.invoice_item)
    ).get_or_404(payment_id)
    # Permission: user must be allowed to view the payment's project
    check_project_permission(payment.invoice.project)

    distributions = []
    for dist in payment.distributions:
        description = dist.invoice_item.description if dist.invoice_item else ''
        distributions.append({
            'description': description,
            'amount': dist.amount
        })

    return jsonify({
        'payment_id': payment.id,
        'distributions': distributions
    })