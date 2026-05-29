from app import db
from datetime import datetime

class MedicalLeave(db.Model):
    __tablename__ = 'medical_leaves'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)  # HIPAA: store only necessary info
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    documents = db.Column(db.JSON)  # S3 keys
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_medical_employee', 'employee_id'),
    )
