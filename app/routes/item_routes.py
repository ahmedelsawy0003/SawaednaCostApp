<<<<<<< HEAD
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.models.project import Project
from app.models.item import Item
from app.extensions import db

item_bp = Blueprint('item', __name__, url_prefix='/items')

@item_bp.route('/project/<int:project_id>', methods=['GET'])
def get_items(project_id):
    project = Project.query.get_or_404(project_id)
    items = Item.query.filter_by(project_id=project_id).order_by(Item.created_at.asc()).all()
    return render_template('items/index.html', project=project, items=items)

@item_bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())

@item_bp.route('/project/<int:project_id>/new', methods=['GET'])
def new_item(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('items/new.html', project=project)

@item_bp.route('/project/<int:project_id>', methods=['POST'])
def create_item(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.form
    try:
        contract_quantity = float(data.get('contract_quantity', 0))
        contract_unit_cost = float(data.get('contract_unit_cost', 0))
        item = Item(
            project_id=project_id,
            item_number=data.get('item_number'),
            description=data.get('description'),
            unit=data.get('unit'),
            contract_quantity=contract_quantity,
            contract_unit_cost=contract_unit_cost,
            contract_total_cost=contract_quantity * contract_unit_cost,
            execution_method=data.get('execution_method'),
            contractor_name=data.get('contractor_name'),
            notes=data.get('notes')
        )
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('item.get_items', project_id=project_id))
    except ValueError:
        return jsonify({'error': 'قيم غير صالحة للكمية أو التكلفة'}), 400

@item_bp.route('/<int:item_id>/edit', methods=['GET'])
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('items/edit.html', item=item)

@item_bp.route('/<int:item_id>', methods=['PUT', 'POST'])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.form
    try:
        item.contract_quantity = float(data.get('contract_quantity'))
        item.contract_unit_cost = float(data.get('contract_unit_cost'))
        item.contract_total_cost = item.contract_quantity * item.contract_unit_cost
        
        # **** هذا هو الجزء الذي تم تعديله ****
        if data.get('actual_quantity'):
            item.actual_quantity = float(data.get('actual_quantity'))
        else:
            item.actual_quantity = None

        if data.get('actual_unit_cost'):
            item.actual_unit_cost = float(data.get('actual_unit_cost'))
        else:
            item.actual_unit_cost = None
        # **** نهاية الجزء المعدل ****

        item.item_number = data.get('item_number', item.item_number)
        item.description = data.get('description', item.description)
        item.unit = data.get('unit', item.unit)
        item.status = data.get('status', item.status)
        item.execution_method = data.get('execution_method', item.execution_method)
        item.contractor_name = data.get('contractor_name', item.contractor_name)
        if data.get('paid_amount'):
            item.paid_amount = float(data.get('paid_amount'))
        item.notes = data.get('notes', item.notes)
        
        db.session.commit()
        return redirect(url_for('item.edit_item', item_id=item_id))
    except (ValueError, TypeError):
        flash('قيم غير صالحة للكمية أو التكلفة.', 'danger')
        return redirect(url_for('item.edit_item', item_id=item_id))

@item_bp.route('/<int:item_id>/delete', methods=['POST'])
=======
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.item import Item
from app.models.project import Project
from app.extensions import db
from flask_login import login_required

item_bp = Blueprint("item", __name__)

@item_bp.route("/projects/<int:project_id>/items")
@login_required
def get_items_by_project(project_id):
    project = Project.query.get_or_404(project_id)
    items = Item.query.filter_by(project_id=project_id).all()
    return render_template("items/index.html", project=project, items=items)

@item_bp.route("/projects/<int:project_id>/items/new", methods=["GET", "POST"])
@login_required
def new_item(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == "POST":
        item_number = request.form["item_number"]
        description = request.form["description"]
        unit = request.form["unit"]
        contract_quantity = float(request.form["contract_quantity"])
        contract_unit_cost = float(request.form["contract_unit_cost"])
        actual_quantity = float(request.form["actual_quantity"]) if request.form["actual_quantity"] else 0.0
        actual_unit_cost = float(request.form["actual_unit_cost"]) if request.form["actual_unit_cost"] else 0.0
        status = request.form["status"]
        execution_method = request.form.get("execution_method")
        contractor = request.form.get("contractor")
        paid_amount = float(request.form["paid_amount"]) if request.form["paid_amount"] else 0.0
        notes = request.form.get("notes")

        new_item = Item(project_id=project_id, item_number=item_number, description=description,
                        unit=unit, contract_quantity=contract_quantity, contract_unit_cost=contract_unit_cost,
                        actual_quantity=actual_quantity, actual_unit_cost=actual_unit_cost, status=status,
                        execution_method=execution_method, contractor=contractor, paid_amount=paid_amount, notes=notes)
        db.session.add(new_item)
        db.session.commit()
        flash("تم إضافة البند بنجاح!", "success")
        return redirect(url_for("item.get_items_by_project", project_id=project_id))
    return render_template("items/new.html", project=project)

@item_bp.route("/items/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    project = Project.query.get_or_404(item.project_id)
    if request.method == "POST":
        item.item_number = request.form["item_number"]
        item.description = request.form["description"]
        item.unit = request.form["unit"]
        item.contract_quantity = float(request.form["contract_quantity"])
        item.contract_unit_cost = float(request.form["contract_unit_cost"])
        item.actual_quantity = float(request.form["actual_quantity"]) if request.form["actual_quantity"] else 0.0
        item.actual_unit_cost = float(request.form["actual_unit_cost"]) if request.form["actual_unit_cost"] else 0.0
        item.status = request.form["status"]
        item.execution_method = request.form.get("execution_method")
        item.contractor = request.form.get("contractor")
        item.paid_amount = float(request.form["paid_amount"]) if request.form["paid_amount"] else 0.0
        item.notes = request.form.get("notes")
        db.session.commit()
        flash("تم تحديث البند بنجاح!", "success")
        return redirect(url_for("item.get_items_by_project", project_id=item.project_id))
    return render_template("items/edit.html", item=item, project=project)

@item_bp.route("/items/<int:item_id>/delete", methods=["POST"])
@login_required
>>>>>>> 7a3713e (Initial commit with updated files)
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    project_id = item.project_id
    db.session.delete(item)
    db.session.commit()
<<<<<<< HEAD
    return redirect(url_for('item.get_items', project_id=project_id))

@item_bp.route('/<int:item_id>/status', methods=['POST'])
def update_item_status(item_id):
    item = Item.query.get_or_404(item_id)
    status = request.form.get('status')
    if not status:
        return jsonify({'error': 'يجب توفير الحالة'}), 400
    item.status = status
    db.session.commit()
    return jsonify(item.to_dict())
=======
    flash("تم حذف البند بنجاح!", "success")
    return redirect(url_for("item.get_items_by_project", project_id=project_id))

@item_bp.route("/items/<int:item_id>/details")
@login_required
def get_item_details(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify({
        "item_number": item.item_number,
        "description": item.description,
        "unit": item.unit,
        "contract_quantity": item.contract_quantity,
        "contract_unit_cost": item.contract_unit_cost,
        "contract_total_cost": item.contract_total_cost,
        "actual_quantity": item.actual_quantity,
        "actual_unit_cost": item.actual_unit_cost,
        "actual_total_cost": item.actual_total_cost,
        "cost_variance": item.cost_variance,
        "quantity_variance": item.quantity_variance,
        "status": item.status,
        "execution_method": item.execution_method,
        "contractor": item.contractor,
        "paid_amount": item.paid_amount,
        "remaining_amount": item.remaining_amount,
        "notes": item.notes
    }))

>>>>>>> 7a3713e (Initial commit with updated files)
