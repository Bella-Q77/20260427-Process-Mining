from flask import Blueprint, jsonify, request, send_file
from models import EventLog, ProcessModel
from extensions import db
import os
from config import Config

mining_bp = Blueprint('mining', __name__)
upload_folder = Config.UPLOAD_FOLDER

_mining_service = None

def get_mining_service():
    global _mining_service
    if _mining_service is None:
        from services.process_mining_service import ProcessMiningService
        _mining_service = ProcessMiningService()
    return _mining_service

@mining_bp.route('/discover', methods=['POST'])
def discover_process():
    """
    发现流程模型
    
    请求体参数:
    - event_log_id: 事件日志ID
    - algorithm: 算法类型 ('alpha', 'inductive', 'heuristics')，默认 'alpha'
    - model_name: 模型名称（可选）
    """
    data = request.get_json() or {}
    
    event_log_id = data.get('event_log_id')
    algorithm = data.get('algorithm', 'alpha')
    model_name = data.get('model_name')
    
    # 验证参数
    if not event_log_id:
        return jsonify({
            'success': False,
            'error': '请提供事件日志ID'
        }), 400
    
    # 检查事件日志是否存在
    event_log = EventLog.query.get(event_log_id)
    if not event_log:
        return jsonify({
            'success': False,
            'error': '事件日志不存在'
        }), 404
    
    # 验证算法类型
    valid_algorithms = ['alpha', 'inductive', 'heuristics']
    if algorithm not in valid_algorithms:
        return jsonify({
            'success': False,
            'error': f'不支持的算法类型。支持的算法: {", ".join(valid_algorithms)}'
        }), 400
    
    try:
        result = get_mining_service().discover_process(
            event_log_id=event_log_id,
            algorithm=algorithm,
            model_name=model_name
        )
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        return jsonify({
            'success': True,
            'message': '流程模型发现成功',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mining_bp.route('/variants/<int:event_log_id>', methods=['GET'])
def get_variants(event_log_id: int):
    """
    获取流程变体分析
    
    参数:
    - event_log_id: 事件日志ID
    """
    # 检查事件日志是否存在
    event_log = EventLog.query.get(event_log_id)
    if not event_log:
        return jsonify({
            'success': False,
            'error': '事件日志不存在'
        }), 404
    
    try:
        result = get_mining_service().get_variants(event_log_id)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        return jsonify({
            'success': True,
            'event_log_id': event_log_id,
            'event_log_name': event_log.name,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mining_bp.route('/performance/<int:event_log_id>', methods=['GET'])
def get_performance(event_log_id: int):
    """
    获取性能分析
    
    参数:
    - event_log_id: 事件日志ID
    """
    # 检查事件日志是否存在
    event_log = EventLog.query.get(event_log_id)
    if not event_log:
        return jsonify({
            'success': False,
            'error': '事件日志不存在'
        }), 404
    
    try:
        result = get_mining_service().get_performance_analysis(event_log_id)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        return jsonify({
            'success': True,
            'event_log_id': event_log_id,
            'event_log_name': event_log.name,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mining_bp.route('/resources/<int:event_log_id>', methods=['GET'])
def get_resource_analysis(event_log_id: int):
    """
    获取资源分析
    
    参数:
    - event_log_id: 事件日志ID
    """
    # 检查事件日志是否存在
    event_log = EventLog.query.get(event_log_id)
    if not event_log:
        return jsonify({
            'success': False,
            'error': '事件日志不存在'
        }), 404
    
    try:
        result = get_mining_service().get_resource_analysis(event_log_id)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        return jsonify({
            'success': True,
            'event_log_id': event_log_id,
            'event_log_name': event_log.name,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mining_bp.route('/departments/<int:event_log_id>', methods=['GET'])
def get_department_analysis(event_log_id: int):
    """
    获取部门分析
    
    参数:
    - event_log_id: 事件日志ID
    """
    # 检查事件日志是否存在
    event_log = EventLog.query.get(event_log_id)
    if not event_log:
        return jsonify({
            'success': False,
            'error': '事件日志不存在'
        }), 404
    
    try:
        result = get_mining_service().get_department_analysis(event_log_id)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        return jsonify({
            'success': True,
            'event_log_id': event_log_id,
            'event_log_name': event_log.name,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mining_bp.route('/algorithms', methods=['GET'])
def get_algorithms_info():
    """
    获取算法信息
    """
    algorithms = [
        {
            'id': 'alpha',
            'name': 'Alpha算法',
            'description': '基于关系的流程发现算法，能够发现活动之间的直接跟随关系，适用于结构化程度较好的流程。',
            'advantages': ['实现简单', '计算速度快', '适合结构化流程'],
            'disadvantages': ['对噪声敏感', '难以处理非结构化流程', '无法发现短循环']
        },
        {
            'id': 'inductive',
            'name': '归纳挖掘算法',
            'description': '基于流程树的发现算法，能够保证发现的模型是健全的（sound），并能处理各种复杂的流程结构。',
            'advantages': ['保证模型健全性', '能处理复杂结构', '抗噪声能力强', '支持分层发现'],
            'disadvantages': ['计算复杂度较高', '可能过度泛化']
        },
        {
            'id': 'heuristics',
            'name': '启发式挖掘算法',
            'description': '基于频率的启发式方法，考虑活动之间的依赖频率，能够过滤低频的噪声行为。',
            'advantages': ['抗噪声能力强', '考虑活动频率', '能发现并发结构', '结果直观易懂'],
            'disadvantages': ['参数设置影响结果', '可能忽略低频但重要的行为']
        }
    ]
    
    return jsonify({
        'success': True,
        'algorithms': algorithms,
        'recommendation': {
            'first_use': '建议首先使用启发式挖掘算法，它对噪声有较好的鲁棒性',
            'structured_process': '如果流程结构清晰，可以使用Alpha算法',
            'complex_process': '如果流程复杂，建议使用归纳挖掘算法'
        }
    })

@mining_bp.route('/model-image/<filename>', methods=['GET'])
def get_model_image(filename: str):
    """
    获取流程模型图片
    
    参数:
    - filename: 图片文件名
    """
    try:
        image_path = os.path.join(upload_folder, filename)
        if not os.path.exists(image_path):
            return jsonify({
                'success': False,
                'error': '图片不存在'
            }), 404
        
        return send_file(image_path, mimetype='image/png')
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
