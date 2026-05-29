from app import db
from sqlalchemy import Index
from datetime import datetime

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # employee, manager, hr_manager, etc.
    salary = db.Column(db.Numeric(10, 2))
    hire_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    location = db.Column(db.String(100))
    employment_type = db.Column(db.String(20))  # full_time, part_time, contract
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Full-text search index
    __table_args__ = (
        Index('idx_employee_full_name', 'first_name', 'last_name', postgresql_using='gin'),
        db.Index('idx_employee_full_text', 
                 db.func.to_tsvector('english', db.func.concat(first_name, ' ', last_name)),
                 postgresql_using='gin')
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'department_id': self.department_id,
            'role': self.role,
            'active': self.active
        }
