from datetime import datetime
from app import db

class EventLog(db.Model):
    """事件日志模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    case_count = db.Column(db.Integer, default=0)
    event_count = db.Column(db.Integer, default=0)
    
    # 关系
    events = db.relationship('Event', backref='event_log', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'case_count': self.case_count,
            'event_count': self.event_count
        }

class Event(db.Model):
    """事件模型"""
    id = db.Column(db.Integer, primary_key=True)
    event_log_id = db.Column(db.Integer, db.ForeignKey('event_log.id'), nullable=False)
    
    # 标准事件日志属性
    case_id = db.Column(db.String(100), nullable=False)  # 案例ID
    activity = db.Column(db.String(100), nullable=False)  # 活动名称
    timestamp = db.Column(db.DateTime, nullable=False)     # 时间戳
    resource = db.Column(db.String(100), nullable=True)    # 资源/负责人
    lifecycle_transition = db.Column(db.String(50), default='complete')  # 生命周期状态
    
    # 财务单据特定属性
    document_type = db.Column(db.String(50), nullable=True)   # 单据类型
    department = db.Column(db.String(100), nullable=True)       # 部门
    amount = db.Column(db.Float, nullable=True)                 # 金额
    status = db.Column(db.String(50), nullable=True)            # 状态
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_log_id': self.event_log_id,
            'case_id': self.case_id,
            'activity': self.activity,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'resource': self.resource,
            'lifecycle_transition': self.lifecycle_transition,
            'document_type': self.document_type,
            'department': self.department,
            'amount': self.amount,
            'status': self.status
        }

class ProcessModel(db.Model):
    """流程模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    algorithm = db.Column(db.String(50), default='alpha')  # 使用的算法
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    event_log_id = db.Column(db.Integer, db.ForeignKey('event_log.id'), nullable=True)
    
    # 存储流程模型的序列化数据
    model_data = db.Column(db.Text, nullable=True)  # JSON格式存储模型数据
    image_path = db.Column(db.String(255), nullable=True)  # 生成的流程图路径
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'algorithm': self.algorithm,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'event_log_id': self.event_log_id,
            'image_path': self.image_path
        }

class AnalysisResult(db.Model):
    """分析结果"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)  # discovery, conformance, enhancement
    event_log_id = db.Column(db.Integer, db.ForeignKey('event_log.id'), nullable=False)
    process_model_id = db.Column(db.Integer, db.ForeignKey('process_model.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 分析结果数据
    result_data = db.Column(db.Text, nullable=True)  # JSON格式存储分析结果
    metrics = db.Column(db.Text, nullable=True)       # JSON格式存储指标
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'analysis_type': self.analysis_type,
            'event_log_id': self.event_log_id,
            'process_model_id': self.process_model_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
