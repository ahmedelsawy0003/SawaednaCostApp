from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.models.project import Project
from app.models.item import Item
from app.extensions import db

item_bp = Blueprint('item', __name__, url_prefix='/items')

@item_bp.route('/project/<int:project_id>', methods=['GET'])
def get_items(project_id):
    """الحصول على قائمة بنود المشروع"""
    project = Project.query.get_or_404(project_id)
    items = Item.query.filter_by(project_id=project_id).order_by(Item.created_at.asc()).all()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify([item.to_dict() for item in items])
    
    return render_template('items/index.html', project=project, items=items)

@item_bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """الحصول على بند محدد"""
    item = Item.query.get_or_404(item_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(item.to_dict())
    
    return render_template('items/show.html', item=item)

@item_bp.route('/project/<int:project_id>/new', methods=['GET'])
def new_item(project_id):
    """عرض نموذج إنشاء بند جديد"""
    project = Project.query.get_or_404(project_id)
    return render_template('items/new.html', project=project)

@item_bp.route('/project/<int:project_id>', methods=['POST'])
def create_item(project_id):
    """إنشاء بند جديد"""
    project = Project.query.get_or_404(project_id)
    data = request.form
    
    if not data.get('item_number') or not data.get('description') or not data.get('unit'):
        return jsonify({'error': 'يجب توفير رقم البند ووصف البند والوحدة'}), 400
    
    try:
        contract_quantity = float(data.get('contract_quantity', 0))
        contract_unit_cost = float(data.get('contract_unit_cost', 0))
        contract_total_cost = contract_quantity * contract_unit_cost
        
        item = Item(
            project_id=project_id,
            item_number=data.get('item_number'),
            description=data.get('description'),
            unit=data.get('unit'),
            contract_quantity=contract_quantity,
            contract_unit_cost=contract_unit_cost,
            contract_total_cost=contract_total_cost,
            execution_method=data.get('execution_method'),
            contractor_name=data.get('contractor_name'),
            notes=data.get('notes')
        )
        
        db.session.add(item)
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(item.to_dict()), 201
        
        return redirect(url_for('item.get_items', project_id=project_id))
    
    except ValueError:
        return jsonify({'error': 'قيم غير صالحة للكمية أو التكلفة'}), 400

@item_bp.route('/<int:item_id>/edit', methods=['GET'])
def edit_item(item_id):
    """عرض نموذج تعديل البند"""
    item = Item.query.get_or_404(item_id)
    return render_template('items/edit.html', item=item)

@item_bp.route('/<int:item_id>', methods=['PUT', 'POST'])
def update_item(item_id):
    """تحديث بند محدد"""
    item = Item.query.get_or_404(item_id)
    data = request.form
    
    try:
        # تحديث البيانات التعاقدية
        if data.get('contract_quantity') and data.get('contract_unit_cost'):
            item.contract_quantity = float(data.get('contract_quantity'))
            item.contract_unit_cost = float(data.get('contract_unit_cost'))
            item.contract_total_cost = item.contract_quantity * item.contract_unit_cost
        
        # **** السطر الجديد لحفظ الكمية الفعلية ****
        if data.get('actual_quantity'):
            item.actual_quantity = float(data.get('actual_quantity'))
        else:
            item.actual_quantity = None
            
        # تحديث بيانات أخرى
        item.item_number = data.get('item_number', item.item_number)
        item.description = data.get('description', item.description)
        item.unit = data.get('unit', item.unit)
        item.status = data.get('status', item.status)
        item.execution_method = data.get('execution_method', item.execution_method)
        item.contractor_name = data.get('contractor_name', item.contractor_name)
        
        if data.get('paid_amount'):
            item.paid_amount = float(data.get('paid_amount'))
        
        item.notes = data.get('notes', item.notes)
        
        # حفظ التغييرات
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(item.to_dict())
        
        return redirect(url_for('item.get_items', project_id=item.project_id))
    
    except ValueError:
        return jsonify({'error': 'قيم غير صالحة للكمية أو التكلفة'}), 400

@item_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """حذف بند محدد"""
    item = Item.query.get_or_404(item_id)
    project_id = item.project_id
    
    db.session.delete(item)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'message': 'تم حذف البند بنجاح'})
    
    return redirect(url_for('item.get_items', project_id=project_id))

@item_bp.route('/<int:item_id>/status', methods=['POST'])
def update_item_status(item_id):
    """تحديث حالة البند"""
    item = Item.query.get_or_404(item_id)
    data = request.form
    
    status = data.get('status')
    if not status:
        return jsonify({'error': 'يجب توفير الحالة'}), 400
    
    if item.update_status(status):
        db.session.commit()
        return jsonify(item.to_dict())
    else:
        return jsonify({'error': 'حالة غير صالحة'}), 400