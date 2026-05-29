from flask import Blueprint, request, jsonify
from app import db
from src.models.audit_log import AuditLog
from src.models.gdpr_request import GDPRRequest
from src.models.medical_leave import MedicalLeave

compliance_bp = Blueprint('compliance', __name__)

@compliance_bp.route('/audit-logs', methods=['GET'])
def get_audit_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=per_page)
    return jsonify({
        'logs': [{
            'id': log.id,
            'user_id': log.user_id,
            'action': log.action,
            'resource_type': log.resource_type,
            'timestamp': log.timestamp.isoformat()
        } for log in logs.items],
        'total': logs.total,
        'page': logs.page
    })

@compliance_bp.route('/gdpr/export', methods=['POST'])
def request_gdpr_export():
    data = request.get_json()
    req = GDPRRequest(user_id=data['user_id'], request_type='export')
    db.session.add(req)
    db.session.commit()
    # Trigger async job to compile and email
    return jsonify({'message': 'Export requested', 'request_id': req.id}), 202

@compliance_bp.route('/gdpr/forget', methods=['POST'])
def request_gdpr_forget():
    data = request.get_json()
    req = GDPRRequest(user_id=data['user_id'], request_type='forget')
    db.session.add(req)
    db.session.commit()
    # Schedule anonymization
    return jsonify({'message': 'Forget requested', 'request_id': req.id}), 202

@compliance_bp.route('/medical-leaves', methods=['GET', 'POST'])
def handle_medical_leaves():
    if request.method == 'POST':
        data = request.get_json()
        leave = MedicalLeave(**data)
        db.session.add(leave)
        db.session.commit()
        return jsonify({'id': leave.id}), 201
    else:
        leaves = MedicalLeave.query.all()
        return jsonify([{'id': l.id, 'employee_id': l.employee_id, 'start_date': l.start_date.isoformat()} for l in leaves])
