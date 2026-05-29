from flask import Blueprint, request, jsonify
from app import db
from src.models.employee import Employee
from sqlalchemy import text
from datetime import datetime

employee_bp = Blueprint('employees', __name__)

@employee_bp.route('', methods=['GET'])
def get_employees():
    # Implement pagination, filtering
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    query = Employee.query.filter(Employee.active == True)
    # Filtering logic here (department, role, hire_date_range, etc.)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'employees': [emp.to_dict() for emp in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })

@employee_bp.route('/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    return jsonify(employee.to_dict())

@employee_bp.route('', methods=['POST'])
def create_employee():
    data = request.get_json()
    employee = Employee(**data)
    db.session.add(employee)
    db.session.commit()
    return jsonify(employee.to_dict()), 201

@employee_bp.route('/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    data = request.get_json()
    for key, value in data.items():
        setattr(employee, key, value)
    db.session.commit()
    return jsonify(employee.to_dict())

@employee_bp.route('/<int:employee_id>/status', methods=['PATCH'])
def update_status(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    data = request.get_json()
    if 'active' in data:
        employee.active = data['active']
        db.session.commit()
    return jsonify(employee.to_dict())

@employee_bp.route('/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    return '', 204

@employee_bp.route('/search', methods=['GET'])
def search_employees():
    q = request.args.get('q', '')
    if not q:
        return jsonify([])
    # Full-text search
    stmt = text("""
        SELECT id, first_name, last_name, email
        FROM employees
        WHERE to_tsvector('english', first_name || ' ' || last_name) @@ plainto_tsquery('english', :q)
        LIMIT 20
    """)
    result = db.session.execute(stmt, {'q': q})
    employees = [dict(row) for row in result]
    return jsonify(employees)
