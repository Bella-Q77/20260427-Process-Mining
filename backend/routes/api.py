from flask import Blueprint, jsonify, request
from models import EventLog, Event, ProcessModel
from extensions import db
from sqlalchemy import func

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'message': '财务单据流程挖掘系统服务正常运行'
    })

@api_bp.route('/event-logs', methods=['GET'])
def get_event_logs():
    """获取所有事件日志列表"""
    logs = EventLog.query.order_by(EventLog.created_at.desc()).all()
    return jsonify([log.to_dict() for log in logs])

@api_bp.route('/event-logs/<int:log_id>', methods=['GET'])
def get_event_log_detail(log_id: int):
    """获取事件日志详情"""
    log = EventLog.query.get_or_404(log_id)
    
    # 获取统计信息
    total_events = Event.query.filter_by(event_log_id=log_id).count()
    total_cases = db.session.query(func.count(func.distinct(Event.case_id))).filter_by(event_log_id=log_id).scalar()
    
    # 获取活动统计
    activity_stats = db.session.query(
        Event.activity,
        func.count(Event.id).label('count')
    ).filter_by(event_log_id=log_id).group_by(Event.activity).all()
    
    return jsonify({
        **log.to_dict(),
        'statistics': {
            'total_events': total_events,
            'total_cases': total_cases,
            'activity_statistics': [{'activity': s.activity, 'count': s.count} for s in activity_stats]
        }
    })

@api_bp.route('/event-logs/<int:log_id>/events', methods=['GET'])
def get_events(log_id: int):
    """获取事件日志中的事件列表（分页）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    log = EventLog.query.get_or_404(log_id)
    
    pagination = Event.query.filter_by(event_log_id=log_id).order_by(
        Event.case_id, Event.timestamp
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'log_id': log_id,
        'log_name': log.name,
        'page': page,
        'per_page': per_page,
        'total': pagination.total,
        'pages': pagination.pages,
        'events': [event.to_dict() for event in pagination.items]
    })

@api_bp.route('/event-logs/<int:log_id>/cases', methods=['GET'])
def get_cases(log_id: int):
    """获取所有案例列表"""
    # 获取所有不重复的案例ID
    cases = db.session.query(
        Event.case_id,
        func.count(Event.id).label('event_count'),
        func.min(Event.timestamp).label('start_time'),
        func.max(Event.timestamp).label('end_time')
    ).filter_by(event_log_id=log_id).group_by(Event.case_id).order_by(
        func.min(Event.timestamp).desc()
    ).all()
    
    return jsonify([{
        'case_id': c.case_id,
        'event_count': c.event_count,
        'start_time': c.start_time.isoformat() if c.start_time else None,
        'end_time': c.end_time.isoformat() if c.end_time else None
    } for c in cases])

@api_bp.route('/event-logs/<int:log_id>/cases/<case_id>', methods=['GET'])
def get_case_detail(log_id: int, case_id: str):
    """获取单个案例的详细信息"""
    events = Event.query.filter_by(
        event_log_id=log_id,
        case_id=case_id
    ).order_by(Event.timestamp).all()
    
    if not events:
        return jsonify({'error': '案例不存在'}), 404
    
    # 计算案例持续时间
    start_time = events[0].timestamp
    end_time = events[-1].timestamp
    duration_seconds = (end_time - start_time).total_seconds()
    
    return jsonify({
        'case_id': case_id,
        'log_id': log_id,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'duration_seconds': duration_seconds,
        'duration_hours': duration_seconds / 3600,
        'event_count': len(events),
        'events': [event.to_dict() for event in events]
    })

@api_bp.route('/process-models', methods=['GET'])
def get_process_models():
    """获取所有流程模型列表"""
    models = ProcessModel.query.order_by(ProcessModel.created_at.desc()).all()
    return jsonify([model.to_dict() for model in models])

@api_bp.route('/process-models/<int:model_id>', methods=['GET'])
def get_process_model_detail(model_id: int):
    """获取流程模型详情"""
    model = ProcessModel.query.get_or_404(model_id)
    return jsonify(model.to_dict())

@api_bp.route('/event-logs/<int:log_id>', methods=['DELETE'])
def delete_event_log(log_id: int):
    """删除事件日志"""
    log = EventLog.query.get_or_404(log_id)
    
    try:
        db.session.delete(log)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'事件日志 "{log.name}" 已删除'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/process-models/<int:model_id>', methods=['DELETE'])
def delete_process_model(model_id: int):
    """删除流程模型"""
    model = ProcessModel.query.get_or_404(model_id)
    
    try:
        db.session.delete(model)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'流程模型 "{model.name}" 已删除'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
