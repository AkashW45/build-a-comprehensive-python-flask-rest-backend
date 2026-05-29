from app import db

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    budget = db.Column(db.Numeric(12, 2), default=0)
    headcount_target = db.Column(db.Integer, default=0)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    employees = db.relationship('Employee', backref='department', lazy='dynamic')
