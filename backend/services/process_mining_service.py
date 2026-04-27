import pandas as pd
import numpy as np
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

from models import EventLog, Event, ProcessModel
from extensions import db
from config import Config

_pm4py_loaded = False
_pm4py_modules = {}

def _load_pm4py():
    global _pm4py_loaded, _pm4py_modules
    if _pm4py_loaded:
        return _pm4py_modules
    
    try:
        import pm4py
        from pm4py.objects.log.util import dataframe_utils
        from pm4py.algo.discovery.alpha import algorithm as alpha_miner
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
        from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness_evaluator
        from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
        from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
        from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator
        from pm4py.algo.filtering.log.variants import variants_filter
        from pm4py.objects.conversion.log import converter as log_converter
        from pm4py.visualization.petri_net import visualizer as pn_visualizer
        from pm4py.visualization.process_tree import visualizer as pt_visualizer
        from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
        
        _pm4py_modules = {
            'pm4py': pm4py,
            'dataframe_utils': dataframe_utils,
            'alpha_miner': alpha_miner,
            'inductive_miner': inductive_miner,
            'heuristics_miner': heuristics_miner,
            'replay_fitness_evaluator': replay_fitness_evaluator,
            'precision_evaluator': precision_evaluator,
            'generalization_evaluator': generalization_evaluator,
            'simplicity_evaluator': simplicity_evaluator,
            'variants_filter': variants_filter,
            'log_converter': log_converter,
            'pn_visualizer': pn_visualizer,
            'pt_visualizer': pt_visualizer,
            'hn_visualizer': hn_visualizer
        }
        
        _pm4py_loaded = True
        return _pm4py_modules
        
    except ImportError as e:
        raise ImportError(
            "pm4py 模块未安装。请运行: pip install pm4py\n"
            "或使用 install.bat 安装所有依赖。"
        ) from e

class ProcessMiningService:
    """流程挖掘服务"""
    
    def __init__(self):
        self.upload_folder = Config.UPLOAD_FOLDER
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    
    def _load_events_to_dataframe(self, event_log_id: int) -> pd.DataFrame:
        events = Event.query.filter_by(event_log_id=event_log_id).order_by(Event.timestamp).all()
        
        if not events:
            return pd.DataFrame()
        
        data = []
        for event in events:
            data.append({
                'case:concept:name': event.case_id,
                'concept:name': event.activity,
                'time:timestamp': event.timestamp,
                'org:resource': event.resource or '',
                'document_type': event.document_type or '',
                'department': event.department or '',
                'amount': event.amount or 0,
                'status': event.status or ''
            })
        
        df = pd.DataFrame(data)
        return df
    
    def _dataframe_to_log(self, df: pd.DataFrame):
        pm = _load_pm4py()
        pm4py = pm['pm4py']
        log_converter = pm['log_converter']
        
        if df.empty:
            return None
        
        df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])
        
        log = pm4py.format_dataframe(
            df,
            case_id='case:concept:name',
            activity_key='concept:name',
            timestamp_key='time:timestamp'
        )
        
        event_log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)
        return event_log
    
    def discover_process(self, event_log_id: int, algorithm: str = 'alpha', model_name: str = None) -> Dict[str, Any]:
        pm = _load_pm4py()
        pm4py = pm['pm4py']
        alpha_miner = pm['alpha_miner']
        inductive_miner = pm['inductive_miner']
        heuristics_miner = pm['heuristics_miner']
        pn_visualizer = pm['pn_visualizer']
        pt_visualizer = pm['pt_visualizer']
        hn_visualizer = pm['hn_visualizer']
        
        df = self._load_events_to_dataframe(event_log_id)
        if df.empty:
            return {'error': '没有找到事件数据'}
        
        event_log = self._dataframe_to_log(df)
        if not event_log:
            return {'error': '无法转换为事件日志'}
        
        net = None
        initial_marking = None
        final_marking = None
        process_tree = None
        heuristics_net = None
        
        if algorithm == 'alpha':
            net, initial_marking, final_marking = alpha_miner.apply(event_log)
        elif algorithm == 'inductive':
            process_tree = inductive_miner.apply(event_log)
            from pm4py.objects.conversion.process_tree import converter as pt_converter
            net, initial_marking, final_marking = pt_converter.apply(process_tree)
        elif algorithm == 'heuristics':
            heuristics_net = heuristics_miner.apply(event_log)
            net, initial_marking, final_marking = heuristics_miner.apply_petri_net(event_log)
        else:
            return {'error': f'不支持的算法: {algorithm}'}
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f'process_model_{event_log_id}_{timestamp}.png'
        image_path = os.path.join(self.upload_folder, image_filename)
        
        if process_tree:
            gviz = pt_visualizer.apply(process_tree)
        elif heuristics_net:
            gviz = hn_visualizer.apply(heuristics_net)
        else:
            gviz = pn_visualizer.apply(net, initial_marking, final_marking)
        
        pn_visualizer.save(gviz, image_path)
        
        metrics = self._calculate_metrics(event_log, net, initial_marking, final_marking)
        
        process_model = ProcessModel(
            name=model_name or f'流程模型_{algorithm}_{timestamp}',
            description=f'使用{self._get_algorithm_name(algorithm)}算法生成的流程模型',
            algorithm=algorithm,
            event_log_id=event_log_id,
            image_path=image_filename,
            model_data=json.dumps({
                'algorithm': algorithm,
                'metrics': metrics,
                'generated_at': datetime.now().isoformat()
            })
        )
        
        db.session.add(process_model)
        db.session.commit()
        
        activities = self._get_activities_from_log(event_log)
        
        return {
            'process_model_id': process_model.id,
            'name': process_model.name,
            'algorithm': algorithm,
            'algorithm_name': self._get_algorithm_name(algorithm),
            'image_path': f'/api/mining/model-image/{image_filename}',
            'metrics': metrics,
            'activities': activities,
            'created_at': process_model.created_at.isoformat()
        }
    
    def _get_algorithm_name(self, algorithm: str) -> str:
        names = {
            'alpha': 'Alpha算法',
            'inductive': '归纳挖掘算法',
            'heuristics': '启发式挖掘算法'
        }
        return names.get(algorithm, algorithm)
    
    def _calculate_metrics(self, event_log, net, initial_marking, final_marking) -> Dict[str, float]:
        pm = _load_pm4py()
        replay_fitness_evaluator = pm['replay_fitness_evaluator']
        precision_evaluator = pm['precision_evaluator']
        generalization_evaluator = pm['generalization_evaluator']
        simplicity_evaluator = pm['simplicity_evaluator']
        
        metrics = {}
        
        try:
            fitness = replay_fitness_evaluator.apply(event_log, net, initial_marking, final_marking)
            metrics['fitness'] = fitness.get('log_fitness', 0) if isinstance(fitness, dict) else fitness
        except Exception:
            metrics['fitness'] = 0.0
        
        try:
            precision = precision_evaluator.apply(event_log, net, initial_marking, final_marking)
            metrics['precision'] = precision
        except Exception:
            metrics['precision'] = 0.0
        
        try:
            generalization = generalization_evaluator.apply(event_log, net, initial_marking, final_marking)
            metrics['generalization'] = generalization
        except Exception:
            metrics['generalization'] = 0.0
        
        try:
            simplicity = simplicity_evaluator.apply(net)
            metrics['simplicity'] = simplicity
        except Exception:
            metrics['simplicity'] = 0.0
        
        return metrics
    
    def _get_activities_from_log(self, event_log) -> List[Dict[str, Any]]:
        activity_counts = defaultdict(int)
        for trace in event_log:
            seen_activities = set()
            for event in trace:
                activity_counts[event['concept:name']] += 1
                seen_activities.add(event['concept:name'])
        
        total_traces = len(event_log)
        activities = []
        for activity, count in activity_counts.items():
            activities.append({
                'name': activity,
                'count': count,
                'trace_coverage': count / total_traces if total_traces > 0 else 0
            })
        
        return sorted(activities, key=lambda x: x['count'], reverse=True)
    
    def get_variants(self, event_log_id: int) -> Dict[str, Any]:
        pm = _load_pm4py()
        variants_filter = pm['variants_filter']
        
        df = self._load_events_to_dataframe(event_log_id)
        if df.empty:
            return {'error': '没有找到事件数据'}
        
        event_log = self._dataframe_to_log(df)
        if not event_log:
            return {'error': '无法转换为事件日志'}
        
        variants = variants_filter.get_variants(event_log)
        
        variant_stats = []
        total_cases = len(event_log)
        
        for variant_string, cases in variants.items():
            case_count = len(cases)
            variant_stats.append({
                'variant': list(variant_string),
                'case_count': case_count,
                'percentage': (case_count / total_cases) * 100 if total_cases > 0 else 0
            })
        
        variant_stats.sort(key=lambda x: x['case_count'], reverse=True)
        
        return {
            'total_variants': len(variant_stats),
            'total_cases': total_cases,
            'variants': variant_stats[:20]
        }
    
    def get_performance_analysis(self, event_log_id: int) -> Dict[str, Any]:
        df = self._load_events_to_dataframe(event_log_id)
        if df.empty:
            return {'error': '没有找到事件数据'}
        
        case_groups = df.groupby('case:concept:name')
        
        case_durations = []
        activity_durations = {}
        
        for case_id, group in case_groups:
            group_sorted = group.sort_values('time:timestamp')
            
            start_time = group_sorted['time:timestamp'].iloc[0]
            end_time = group_sorted['time:timestamp'].iloc[-1]
            duration_hours = (end_time - start_time).total_seconds() / 3600
            case_durations.append(duration_hours)
            
            activities = group_sorted['concept:name'].tolist()
            timestamps = group_sorted['time:timestamp'].tolist()
            
            for i in range(len(activities) - 1):
                current_activity = activities[i]
                next_activity = activities[i + 1]
                wait_time = (timestamps[i + 1] - timestamps[i]).total_seconds() / 3600
                
                key = f'{current_activity}->{next_activity}'
                if key not in activity_durations:
                    activity_durations[key] = []
                activity_durations[key].append(wait_time)
        
        duration_stats = {
            'min': min(case_durations) if case_durations else 0,
            'max': max(case_durations) if case_durations else 0,
            'mean': np.mean(case_durations) if case_durations else 0,
            'median': np.median(case_durations) if case_durations else 0,
            'count': len(case_durations)
        }
        
        activity_wait_stats = []
        for path, times in activity_durations.items():
            activity_wait_stats.append({
                'path': path,
                'min': min(times),
                'max': max(times),
                'mean': np.mean(times),
                'median': np.median(times),
                'count': len(times)
            })
        
        activity_wait_stats.sort(key=lambda x: x['mean'], reverse=True)
        
        activity_counts = df['concept:name'].value_counts().to_dict()
        
        return {
            'case_duration_statistics': duration_stats,
            'activity_wait_times': activity_wait_stats[:10],
            'activity_counts': activity_counts,
            'total_cases': len(case_durations)
        }
    
    def get_resource_analysis(self, event_log_id: int) -> Dict[str, Any]:
        df = self._load_events_to_dataframe(event_log_id)
        if df.empty:
            return {'error': '没有找到事件数据'}
        
        resource_stats = df.groupby('org:resource').agg({
            'case:concept:name': 'nunique',
            'concept:name': 'count'
        }).rename(columns={
            'case:concept:name': 'case_count',
            'concept:name': 'activity_count'
        }).reset_index()
        
        resource_activity_dist = df.groupby(['org:resource', 'concept:name']).size().unstack(fill_value=0)
        
        return {
            'resource_statistics': resource_stats.to_dict('records'),
            'resource_activity_distribution': resource_activity_dist.to_dict('index')
        }
    
    def get_department_analysis(self, event_log_id: int) -> Dict[str, Any]:
        df = self._load_events_to_dataframe(event_log_id)
        if df.empty:
            return {'error': '没有找到事件数据'}
        
        dept_cases = df.groupby('department')['case:concept:name'].nunique().reset_index(name='case_count')
        
        maker_df = df[df['concept:name'] == '制单']
        if not maker_df.empty:
            dept_amount = maker_df.groupby('department')['amount'].agg({
                'total_amount': 'sum',
                'avg_amount': 'mean',
                'min_amount': 'min',
                'max_amount': 'max'
            }).reset_index()
        else:
            dept_amount = pd.DataFrame(columns=['department', 'total_amount', 'avg_amount', 'min_amount', 'max_amount'])
        
        dept_activity = df.groupby(['department', 'concept:name']).size().unstack(fill_value=0)
        
        return {
            'department_cases': dept_cases.to_dict('records'),
            'department_amounts': dept_amount.to_dict('records'),
            'department_activity_distribution': dept_activity.to_dict('index')
        }
