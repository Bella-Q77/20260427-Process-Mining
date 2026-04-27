from flask import Blueprint, jsonify, request
from services.simulation_service import SimulationService
from models import EventLog
from app import db

simulation_bp = Blueprint('simulation', __name__)
simulation_service = SimulationService()

@simulation_bp.route('/generate', methods=['POST'])
def generate_simulation_data():
    """
    生成模拟数据
    
    请求体参数:
    - num_cases: 案例数量 (默认: 100)
    - log_name: 日志名称 (默认: '模拟财务单据流程日志')
    """
    data = request.get_json() or {}
    
    num_cases = data.get('num_cases', 100)
    log_name = data.get('log_name', '模拟财务单据流程日志')
    
    # 验证参数
    try:
        num_cases = int(num_cases)
        if num_cases < 1 or num_cases > 10000:
            return jsonify({
                'success': False,
                'error': '案例数量必须在1到10000之间'
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            'success': False,
            'error': '案例数量必须是整数'
        }), 400
    
    try:
        result = simulation_service.generate_simulation_data(
            num_cases=num_cases,
            log_name=log_name
        )
        
        return jsonify({
            'success': True,
            'message': f'成功生成{num_cases}个案例的模拟数据',
            'data': result
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@simulation_bp.route('/statistics/<int:event_log_id>', methods=['GET'])
def get_simulation_statistics(event_log_id: int):
    """
    获取模拟数据的统计信息
    
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
        stats = simulation_service.get_process_statistics(event_log_id)
        
        return jsonify({
            'success': True,
            'event_log_id': event_log_id,
            'event_log_name': event_log.name,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@simulation_bp.route('/variants', methods=['POST'])
def get_process_variants_info():
    """
    获取流程变体信息（模拟数据的变体说明）
    """
    variants_info = {
        'normal': {
            'name': '正常流程',
            'description': '标准的财务单据审批流程：制单 -> 部门审核 -> 财务审核 -> 支付 -> 归档',
            'percentage': '50%',
            'activities': ['制单', '部门审核', '财务审核', '支付', '归档']
        },
        'rework': {
            'name': '返工流程',
            'description': '包含驳回修改的流程：制单 -> 部门审核(驳回) -> 制单(修改) -> 部门审核(通过) -> 财务审核 -> 支付 -> 归档',
            'percentage': '20%',
            'activities': ['制单', '部门审核', '制单', '部门审核', '财务审核', '支付', '归档']
        },
        'approval_required': {
            'name': '大额审批流程',
            'description': '金额超过5万元需要总经理审批的流程：制单 -> 部门审核 -> 财务审核 -> 总经理审批 -> 支付 -> 归档',
            'percentage': '20%',
            'activities': ['制单', '部门审核', '财务审核', '总经理审批', '支付', '归档']
        },
        'rework_approval': {
            'name': '返工+审批流程',
            'description': '既有驳回修改又需要总经理审批的复杂流程',
            'percentage': '8%',
            'activities': ['制单', '部门审核', '财务审核(驳回)', '制单(修改)', '财务审核(通过)', '总经理审批', '支付', '归档']
        },
        'skipped_step': {
            'name': '异常流程',
            'description': '跳过审核步骤的异常流程（用于展示流程挖掘的检测能力）：制单 -> 支付 -> 归档',
            'percentage': '2%',
            'activities': ['制单', '支付', '归档']
        }
    }
    
    return jsonify({
        'success': True,
        'variants': variants_info,
        'description': '模拟数据集包含5种不同的流程变体，覆盖正常、返工、审批、异常等多种业务场景'
    })

@simulation_bp.route('/sample-data', methods=['GET'])
def get_sample_data_structure():
    """
    获取模拟数据的结构说明
    """
    sample_structure = {
        'event_fields': {
            'case_id': '案例ID，用于唯一标识一个财务单据的整个生命周期',
            'activity': '活动名称，如：制单、部门审核、财务审核、总经理审批、支付、归档',
            'timestamp': '事件发生的时间戳',
            'resource': '执行该活动的人员',
            'document_type': '单据类型，如：报销单、付款单、采购申请单等',
            'department': '所属部门，如：销售部、技术部、财务部等',
            'amount': '单据金额（元）',
            'status': '事件状态，如：提交、通过、驳回、修改后提交等'
        },
        'document_types': [
            '报销单',
            '付款单', 
            '采购申请单',
            '差旅费报销单',
            '借款单',
            '费用报销单'
        ],
        'departments': [
            '销售部',
            '技术部',
            '财务部',
            '行政部',
            '人力资源部',
            '市场部',
            '研发部'
        ],
        'typical_approval_rules': {
            '金额小于5万元': '制单 -> 部门审核 -> 财务审核 -> 支付 -> 归档',
            '金额大于等于5万元': '制单 -> 部门审核 -> 财务审核 -> 总经理审批 -> 支付 -> 归档',
            '审核不通过': '返回制单环节修改后重新提交'
        }
    }
    
    return jsonify({
        'success': True,
        'data_structure': sample_structure
    })
