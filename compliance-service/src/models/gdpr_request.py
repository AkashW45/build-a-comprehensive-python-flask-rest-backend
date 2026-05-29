from app import db
from datetime import datetime

class GDPRRequest(db.Model):
    __tablename__ = 'gdpr_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    request_type = db.Column(db.String(20))  # 'export', 'forget'
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    data_payload = db.Column(db.JSON)  # for export
