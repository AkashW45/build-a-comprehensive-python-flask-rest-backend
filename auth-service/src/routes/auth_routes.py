from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from app import db, jwt
from src.models.user import User
from src.models.mfa import MFA
import pyotp
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'msg': 'Username already exists'}), 409
    user = User(username=data['username'], email=data['email'], role=data.get('role', 'employee'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': 'User created'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'msg': 'Invalid credentials'}), 401
    
    # Check password policy (implement validation elsewhere)
    
    # Check if MFA required
    if user.mfa_enabled:
        # Return a temporary token to get the MFA code
        temp_token = create_access_token(identity=user.id, additional_claims={'mfa_required': True}, expires_delta=datetime.timedelta(minutes=5))
        return jsonify({'mfa_required': True, 'temp_token': temp_token}), 200
    
    access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

@auth_bp.route('/mfa/verify', methods=['POST'])
@jwt_required()
def verify_mfa():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    mfa = MFA.query.filter_by(user_id=current_user_id).first()
    if not mfa:
        return jsonify({'msg': 'MFA not configured'}), 400
    totp = pyotp.TOTP(mfa.secret)
    if totp.verify(data['code']):
        access_token = create_access_token(identity=current_user_id, additional_claims={'role': User.query.get(current_user_id).role})
        refresh_token = create_refresh_token(identity=current_user_id)
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    return jsonify({'msg': 'Invalid code'}), 401

@auth_bp.route('/mfa/setup', methods=['POST'])
@jwt_required()
def setup_mfa():
    user_id = get_jwt_identity()
    secret = pyotp.random_base32()
    mfa = MFA(user_id=user_id, secret=secret, enabled=True)
    db.session.add(mfa)
    db.session.commit()
    return jsonify({'secret': secret, 'qr_url': pyotp.totp.TOTP(secret).provisioning_uri(name=User.query.get(user_id).email, issuer_name='HR System')}), 201

@auth_bp.route('/sso/login', methods=['POST'])
def sso_login():
    # SAML SSO integration placeholder
    return jsonify({'msg': 'SAML SSO flow not yet implemented'}), 501

@jwt.user_identity_loader
def user_identity_lookup(user_id):
    return user_id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data['sub']
    return User.query.get(identity)
