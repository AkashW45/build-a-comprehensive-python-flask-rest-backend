from flask import Blueprint, request, jsonify, Response
import requests
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from functools import wraps

proxy_bp = Blueprint('proxy', __name__)

# Service URLs (from environment)
EMPLOYEE_SERVICE_URL = 'http://employee-service:5001'
DEPARTMENT_SERVICE_URL = 'http://department-service:5002'
PAYROLL_SERVICE_URL = 'http://payroll-service:5003'
LEAVE_SERVICE_URL = 'http://leave-service:5004'
PERFORMANCE_SERVICE_URL = 'http://performance-service:5005'
RECRUITMENT_SERVICE_URL = 'http://recruitment-service:5006'
INTEGRATION_SERVICE_URL = 'http://integration-service:5007'
COMPLIANCE_SERVICE_URL = 'http://compliance-service:5008'

def proxy_request(service_url, path):
    """Proxy the request to the appropriate microservice"""
    url = f"{service_url}{path}"
    method = request.method.lower()
    headers = {key: value for key, value in request.headers if key != 'Host'}
    resp = requests.request(method, url, headers=headers, data=request.get_data(), params=request.args)
    return Response(resp.content, resp.status_code, resp.headers.items())

@proxy_bp.route('/employees', defaults={'path': ''}, methods=['GET', 'POST'])
@proxy_bp.route('/employees/<path:path>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@jwt_required()
def proxy_employees(path):
    return proxy_request(EMPLOYEE_SERVICE_URL, f'/employees/{path}')

@proxy_bp.route('/departments', defaults={'path': ''}, methods=['GET', 'POST'])
@proxy_bp.route('/departments/<path:path>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def proxy_departments(path):
    return proxy_request(DEPARTMENT_SERVICE_URL, f'/departments/{path}')

@proxy_bp.route('/payroll', defaults={'path': ''}, methods=['GET', 'POST'])
@proxy_bp.route('/payroll/<path:path>', methods=['GET', 'POST'])
@jwt_required()
def proxy_payroll(path):
    return proxy_request(PAYROLL_SERVICE_URL, f'/payroll/{path}')

@proxy_bp.route('/leaves', defaults={'path': ''}, methods=['GET', 'POST'])
@proxy_bp.route('/leaves/<path:path>', methods=['GET', 'PUT'])
@jwt_required()
def proxy_leaves(path):
    return proxy_request(LEAVE_SERVICE_URL, f'/leaves/{path}')

@proxy_bp.route('/reviews', defaults={'path': ''}, methods=['GET', 'POST'])
@proxy_bp.route('/reviews/<path:path>', methods=['GET', 'PUT', 'POST'])
@jwt_required()
def proxy_reviews(path):
    return proxy_request(PERFORMANCE_SERVICE_URL, f'/reviews/{path}')

@proxy_bp.route('/recruitment', defaults={'path': ''}, methods=['GET', 'POST'])
@proxy_bp.route('/recruitment/<path:path>', methods=['GET', 'PUT'])
@jwt_required()
def proxy_recruitment(path):
    return proxy_request(RECRUITMENT_SERVICE_URL, f'/recruitment/{path}')

@proxy_bp.route('/integrations', defaults={'path': ''}, methods=['POST'])
@proxy_bp.route('/integrations/<path:path>', methods=['POST'])
@jwt_required()
def proxy_integrations(path):
    return proxy_request(INTEGRATION_SERVICE_URL, f'/integrations/{path}')

@proxy_bp.route('/compliance', defaults={'path': ''}, methods=['GET', 'POST', 'DELETE'])
@proxy_bp.route('/compliance/<path:path>', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def proxy_compliance(path):
    return proxy_request(COMPLIANCE_SERVICE_URL, f'/compliance/{path}')
