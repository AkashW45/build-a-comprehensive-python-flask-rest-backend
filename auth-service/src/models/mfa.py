from app import db

class MFA(db.Model):
    __tablename__ = 'mfa'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    secret = db.Column(db.String(32), nullable=False)
    method = db.Column(db.String(20), default='totp')  # totp, sms, email
    enabled = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref=db.backref('mfa_settings', lazy=True))
