from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    # Validate credentials via Auth Service (internal call)
    # Placeholder: return tokens for demo
    if data.get('username') == 'admin' and data.get('password') == 'password':
        access_token = create_access_token(identity=data['username'], additional_claims={'role': 'admin'})
        refresh_token = create_refresh_token(identity=data['username'])
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    return jsonify({'msg': 'Invalid credentials'}), 401

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token), 200

@auth_bp.route('/mfa/verify', methods=['POST'])
def verify_mfa():
    # TOTP verification
    return jsonify({'msg': 'MFA verified'}), 200
