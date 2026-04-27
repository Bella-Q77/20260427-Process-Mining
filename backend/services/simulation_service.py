import random
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models import EventLog, Event
from app import db

class SimulationService:
    """模拟数据生成服务"""
    
    def __init__(self):
        # 定义财务单据流程的基本活动
        self.base_activities = [
            '制单',
            '部门审核',
            '财务审核',
            '总经理审批',
            '支付',
            '归档'
        ]
        
        # 定义单据类型
        self.document_types = [
            '报销单',
            '付款单',
            '采购申请单',
            '差旅费报销单',
            '借款单',
            '费用报销单'
        ]
        
        # 定义部门
        self.departments = [
            '销售部',
            '技术部',
            '财务部',
            '行政部',
            '人力资源部',
            '市场部',
            '研发部'
        ]
        
        # 定义资源（审核人员）
        self.resources = {
            '制单': ['张三', '李四', '王五', '赵六', '钱七'],
            '部门审核': ['销售经理', '技术主管', '财务主管', '行政经理', 'HR经理', '市场总监', '研发经理'],
            '财务审核': ['张会计', '李会计', '王财务', '赵出纳'],
            '总经理审批': ['王总', '李总'],
            '支付': ['赵出纳', '李出纳'],
            '归档': ['档案管理员A', '档案管理员B']
        }
        
        # 定义不同流程变体
        self.process_variants = {
            'normal': self._generate_normal_flow,
            'rework': self._generate_rework_flow,
            'approval_required': self._generate_approval_flow,
            'rework_approval': self._generate_rework_approval_flow,
            'skipped_step': self._generate_skipped_flow
        }
    
    def generate_simulation_data(self, num_cases: int = 100, log_name: str = '模拟财务单据流程日志') -> Dict[str, Any]:
        """
        生成模拟数据
        
        Args:
            num_cases: 案例数量
            log_name: 日志名称
            
        Returns:
            生成的事件日志信息
        """
        # 创建事件日志
        event_log = EventLog(
            name=log_name,
            description=f'自动生成的模拟财务单据流程数据，共{num_cases}个案例',
            case_count=0,
            event_count=0
        )
        db.session.add(event_log)
        db.session.flush()
        
        all_events = []
        case_count = 0
        event_count = 0
        
        # 根据比例分配不同的流程变体
        variant_distribution = {
            'normal': 0.5,      # 50% 正常流程
            'rework': 0.2,      # 20% 有返工的流程
            'approval_required': 0.2,  # 20% 需要总经理审批的大额流程
            'rework_approval': 0.08,   # 8% 有返工且需要审批的流程
            'skipped_step': 0.02       # 2% 有跳过步骤的流程（异常情况）
        }
        
        for i in range(num_cases):
            # 随机选择流程变体
            variant = self._select_variant(variant_distribution)
            case_id = f'CASE_{i+1:06d}'
            
            # 生成案例数据
            events = self.process_variants[variant](case_id)
            all_events.extend(events)
            case_count += 1
            event_count += len(events)
            
            # 批量插入数据库
            if len(all_events) >= 1000:
                self._bulk_insert_events(event_log.id, all_events)
                all_events = []
        
        # 插入剩余的事件
        if all_events:
            self._bulk_insert_events(event_log.id, all_events)
        
        # 更新事件日志统计信息
        event_log.case_count = case_count
        event_log.event_count = event_count
        db.session.commit()
        
        return {
            'event_log_id': event_log.id,
            'name': event_log.name,
            'case_count': case_count,
            'event_count': event_count
        }
    
    def _select_variant(self, distribution: Dict[str, float]) -> str:
        """根据分布选择流程变体"""
        rand = random.random()
        cumulative = 0.0
        for variant, prob in distribution.items():
            cumulative += prob
            if rand <= cumulative:
                return variant
        return 'normal'
    
    def _generate_normal_flow(self, case_id: str) -> List[Dict[str, Any]]:
        """生成正常流程：制单 -> 部门审核 -> 财务审核 -> 支付 -> 归档"""
        events = []
        base_time = datetime.now() - timedelta(days=random.randint(30, 90))
        
        # 随机选择单据类型和部门
        doc_type = random.choice(self.document_types)
        dept = random.choice(self.departments)
        amount = round(random.uniform(100, 50000), 2)
        
        # 活动序列
        activity_sequence = ['制单', '部门审核', '财务审核', '支付', '归档']
        
        for activity in activity_sequence:
            # 随机生成时间间隔
            time_delta = timedelta(
                hours=random.randint(1, 72),
                minutes=random.randint(0, 59)
            )
            base_time += time_delta
            
            # 随机选择资源
            resource = random.choice(self.resources[activity])
            
            events.append({
                'case_id': case_id,
                'activity': activity,
                'timestamp': base_time,
                'resource': resource,
                'document_type': doc_type,
                'department': dept,
                'amount': amount,
                'status': '完成'
            })
        
        return events
    
    def _generate_rework_flow(self, case_id: str) -> List[Dict[str, Any]]:
        """生成有返工的流程：制单 -> 部门审核 -> 制单（修改）-> 部门审核 -> 财务审核 -> 支付 -> 归档"""
        events = []
        base_time = datetime.now() - timedelta(days=random.randint(30, 90))
        
        doc_type = random.choice(self.document_types)
        dept = random.choice(self.departments)
        amount = round(random.uniform(100, 50000), 2)
        
        # 制单
        time_delta = timedelta(hours=random.randint(1, 24), minutes=random.randint(0, 59))
        base_time += time_delta
        events.append({
            'case_id': case_id,
            'activity': '制单',
            'timestamp': base_time,
            'resource': random.choice(self.resources['制单']),
            'document_type': doc_type,
            'department': dept,
            'amount': amount,
            'status': '提交'
        })
        
        # 部门审核（第一次，驳回）
        time_delta = timedelta(hours=random.randint(1, 48), minutes=random.randint(0, 59))
        base_time += time_delta
        events.append({
            'case_id': case_id,
            'activity': '部门审核',
            'timestamp': base_time,
            'resource': random.choice(self.resources['部门审核']),
            'document_type': doc_type,
            'department': dept,
            'amount': amount,
            'status': '驳回'
        })
        
        # 制单（修改）
        time_delta = timedelta(hours=random.randint(1, 72), minutes=random.randint(0, 59))
        base_time += time_delta
        events.append({
            'case_id': case_id,
            'activity': '制单',
            'timestamp': base_time,
            'resource': events[0]['resource'],
            'document_type': doc_type,
            'department': dept,
            'amount': amount,
            'status': '修改后提交'
        })
        
        # 部门审核（第二次，通过）
        time_delta = timedelta(hours=random.randint(1, 48), minutes=random.randint(0, 59))
        base_time += time_delta
        events.append({
            'case_id': case_id,
            'activity': '部门审核',
            'timestamp': base_time,
            'resource': random.choice(self.resources['部门审核']),
            'document_type': doc_type,
            'department': dept,
            'amount': amount,
            'status': '通过'
        })
        
        # 后续正常流程
        for activity in ['财务审核', '支付', '归档']:
            time_delta = timedelta(hours=random.randint(1, 72), minutes=random.randint(0, 59))
            base_time += time_delta
            events.append({
                'case_id': case_id,
                'activity': activity,
                'timestamp': base_time,
                'resource': random.choice(self.resources[activity]),
                'document_type': doc_type,
                'department': dept,
                'amount': amount,
                'status': '完成'
            })
        
        return events
    
    def _generate_approval_flow(self, case_id: str) -> List[Dict[str, Any]]:
        """生成需要总经理审批的大额流程：制单 -> 部门审核 -> 财务审核 -> 总经理审批 -> 支付 -> 归档"""
        events = []
        base_time = datetime.now() - timedelta(days=random.randint(30, 90))
        
        doc_type = random.choice(self.document_types)
        dept = random.choice(self.departments)
        # 大额金额
        amount = round(random.uniform(50000, 500000), 2)
        
        # 活动序列
        activity_sequence = ['制单', '部门审核', '财务审核', '总经理审批', '支付', '归档']
        
        for activity in activity_sequence:
            time_delta = timedelta(
                hours=random.randint(1, 120),
                minutes=random.randint(0, 59)
            )
            base_time += time_delta
            
            events.append({
                'case_id': case_id,
                'activity': activity,
                'timestamp': base_time,
                'resource': random.choice(self.resources[activity]),
                'document_type': doc_type,
                'department': dept,
                'amount': amount,
                'status': '完成'
            })
        
        return events
    
    def _generate_rework_approval_flow(self, case_id: str) -> List[Dict[str, Any]]:
        """生成有返工且需要审批的流程"""
        events = []
        base_time = datetime.now() - timedelta(days=random.randint(30, 90))
        
        doc_type = random.choice(self.document_types)
        dept = random.choice(self.departments)
        amount = round(random.uniform(50000, 500000), 2)
        
        # 制单
        time_delta = timedelta(hours=random.randint(1, 24), minutes=random.randint(0, 59))
        base_time += time_delta
        maker = random.choice(self.resources['制单'])
        events.append({
            'case_id': case_id,
            'activity': '制单',
            'timestamp': base_time,
            'resource': maker,
            'document_type': doc_type,
            'department': dept,
            'amount': amount,
            'status': '提交'
        })
        
        # 部门审核（通过）
        time_delta = timedelta(hours=random.randint(1, 48), minutes=random.randint(0, 59))
        base_time += time_delta
        events.append({
            'case_id': case_id,
            'activity': '部门审核',
            'timestamp': base_time,
            'resource': random.choice(self.resources['部门审核']),
            'document_type': doc_type,
            'department': dept,
            'amount': amount,
            'status': '通过'
        })
        
        # 财务审核（驳回）
        time_delta = timedelta(hours=random.randint(1, 48), minutes=random.randint(0, 59))
        base_time += time_delta
        events.append({
            'case_id': case_id,
            'activity': '财务审核',
            'timestamp': base_time,
            'resource': random.choice(self.resources['财务审核']),
            'document_type': doc_type,
            'department': dept,
            'amount': amount,
            'status': '驳回'
        })
        
        # 制单（修改）
        time_delta = timedelta(hours=random.randint(1, 72), minutes=random.randint(0, 59))
        base_time += time_delta
        events.append({
            'case_id': case_id,
            'activity': '制单',
            'timestamp': base_time,
            'resource': maker,
            'document_type': doc_type,
            'department': dept,
            'amount': amount,
            'status': '修改后提交'
        })
        
        # 财务审核（通过）
        time_delta = timedelta(hours=random.randint(1, 48), minutes=random.randint(0, 59))
        base_time += time_delta
        events.append({
            'case_id': case_id,
            'activity': '财务审核',
            'timestamp': base_time,
            'resource': random.choice(self.resources['财务审核']),
            'document_type': doc_type,
            'department': dept,
            'amount': amount,
            'status': '通过'
        })
        
        # 后续流程
        for activity in ['总经理审批', '支付', '归档']:
            time_delta = timedelta(hours=random.randint(1, 120), minutes=random.randint(0, 59))
            base_time += time_delta
            events.append({
                'case_id': case_id,
                'activity': activity,
                'timestamp': base_time,
                'resource': random.choice(self.resources[activity]),
                'document_type': doc_type,
                'department': dept,
                'amount': amount,
                'status': '完成'
            })
        
        return events
    
    def _generate_skipped_flow(self, case_id: str) -> List[Dict[str, Any]]:
        """生成有跳过步骤的异常流程：制单 -> 支付 -> 归档（跳过审核）"""
        events = []
        base_time = datetime.now() - timedelta(days=random.randint(30, 90))
        
        doc_type = random.choice(self.document_types)
        dept = random.choice(self.departments)
        amount = round(random.uniform(100, 10000), 2)
        
        # 制单
        time_delta = timedelta(hours=random.randint(1, 24), minutes=random.randint(0, 59))
        base_time += time_delta
        events.append({
            'case_id': case_id,
            'activity': '制单',
            'timestamp': base_time,
            'resource': random.choice(self.resources['制单']),
            'document_type': doc_type,
            'department': dept,
            'amount': amount,
            'status': '提交'
        })
        
        # 跳过审核，直接支付（异常情况）
        time_delta = timedelta(hours=random.randint(1, 48), minutes=random.randint(0, 59))
        base_time += time_delta
        events.append({
            'case_id': case_id,
            'activity': '支付',
            'timestamp': base_time,
            'resource': random.choice(self.resources['支付']),
            'document_type': doc_type,
            'department': dept,
            'amount': amount,
            'status': '异常支付'
        })
        
        # 归档
        time_delta = timedelta(hours=random.randint(1, 24), minutes=random.randint(0, 59))
        base_time += time_delta
        events.append({
            'case_id': case_id,
            'activity': '归档',
            'timestamp': base_time,
            'resource': random.choice(self.resources['归档']),
            'document_type': doc_type,
            'department': dept,
            'amount': amount,
            'status': '已归档'
        })
        
        return events
    
    def _bulk_insert_events(self, event_log_id: int, events: List[Dict[str, Any]]):
        """批量插入事件到数据库"""
        db_events = []
        for event in events:
            db_event = Event(
                event_log_id=event_log_id,
                case_id=event['case_id'],
                activity=event['activity'],
                timestamp=event['timestamp'],
                resource=event['resource'],
                document_type=event['document_type'],
                department=event['department'],
                amount=event['amount'],
                status=event['status']
            )
            db_events.append(db_event)
        
        db.session.add_all(db_events)
        db.session.commit()
    
    def get_process_statistics(self, event_log_id: int) -> Dict[str, Any]:
        """获取流程统计信息"""
        from sqlalchemy import func
        
        # 基本统计
        total_events = Event.query.filter_by(event_log_id=event_log_id).count()
        total_cases = db.session.query(func.count(func.distinct(Event.case_id))).filter_by(event_log_id=event_log_id).scalar()
        
        # 按活动统计
        activity_stats = db.session.query(
            Event.activity,
            func.count(Event.id).label('count'),
            func.count(func.distinct(Event.case_id)).label('case_count')
        ).filter_by(event_log_id=event_log_id).group_by(Event.activity).all()
        
        # 按部门统计
        department_stats = db.session.query(
            Event.department,
            func.count(func.distinct(Event.case_id)).label('case_count')
        ).filter_by(event_log_id=event_log_id).group_by(Event.department).all()
        
        # 按单据类型统计
        doc_type_stats = db.session.query(
            Event.document_type,
            func.count(func.distinct(Event.case_id)).label('case_count')
        ).filter_by(event_log_id=event_log_id).group_by(Event.document_type).all()
        
        # 金额统计
        amount_stats = db.session.query(
            func.min(Event.amount).label('min_amount'),
            func.max(Event.amount).label('max_amount'),
            func.avg(Event.amount).label('avg_amount'),
            func.sum(Event.amount).label('total_amount')
        ).filter(Event.event_log_id == event_log_id, Event.activity == '制单').first()
        
        return {
            'total_events': total_events,
            'total_cases': total_cases,
            'activity_statistics': [{'activity': s.activity, 'count': s.count, 'case_count': s.case_count} for s in activity_stats],
            'department_statistics': [{'department': s.department, 'case_count': s.case_count} for s in department_stats],
            'document_type_statistics': [{'document_type': s.document_type, 'case_count': s.case_count} for s in doc_type_stats],
            'amount_statistics': {
                'min': float(amount_stats.min_amount) if amount_stats.min_amount else 0,
                'max': float(amount_stats.max_amount) if amount_stats.max_amount else 0,
                'avg': float(amount_stats.avg_amount) if amount_stats.avg_amount else 0,
                'total': float(amount_stats.total_amount) if amount_stats.total_amount else 0
            }
        }
