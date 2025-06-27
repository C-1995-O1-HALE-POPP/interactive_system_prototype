"""
情绪标注与报告生成模块
实现回忆分类、情绪轨迹报告、可视化图表生成等功能
"""

import json
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import seaborn as sns
from ris_data_model import RISDataModel

import io
import base64

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class EmotionReportGenerator:
    """情绪报告生成器"""
    
    def __init__(self, db_path: str = "ris_system.db"):
        """
        初始化报告生成器
        
        Args:
            db_path: 数据库路径
        """
        self.ris_model = RISDataModel(db_path)
        
        # 设置图表样式
        sns.set_style("whitegrid")
        plt.style.use('seaborn-v0_8')
        
        print("情绪报告生成器初始化完成")
    
    def classify_memories_by_emotion(self, user_id: str, time_range: int = 30) -> Dict[str, Any]:
        """
        根据情感对回忆进行分类
        
        Args:
            user_id: 用户ID
            time_range: 时间范围（天数）
            
        Returns:
            Dict: 分类结果
        """
        # 获取指定时间范围内的回忆
        memories = self.ris_model.get_memory_events(user_id, limit=1000)
        
        # 过滤时间范围
        cutoff_date = datetime.now() - timedelta(days=time_range)
        filtered_memories = []
        
        for memory in memories:
            try:
                memory_date = datetime.fromisoformat(memory['created_at'].replace('Z', '+00:00'))
                if memory_date >= cutoff_date:
                    filtered_memories.append(memory)
            except:
                continue
        
        # 分类统计
        classification = {
            'positive': [],
            'negative': [],
            'neutral': [],
            'statistics': {
                'total_memories': len(filtered_memories),
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'time_range_days': time_range
            },
            'detailed_analysis': {}
        }
        
        # 按情感类型分类
        for memory in filtered_memories:
            memory_type = memory.get('memory_type', 'neutral')
            classification[memory_type].append(memory)
            classification['statistics'][f'{memory_type}_count'] += 1
        
        # 计算比例
        total = classification['statistics']['total_memories']
        if total > 0:
            classification['statistics']['positive_ratio'] = classification['statistics']['positive_count'] / total
            classification['statistics']['negative_ratio'] = classification['statistics']['negative_count'] / total
            classification['statistics']['neutral_ratio'] = classification['statistics']['neutral_count'] / total
        
        # 详细分析
        classification['detailed_analysis'] = self._analyze_memory_patterns(filtered_memories)
        
        return classification
    
    def generate_weekly_report(self, user_id: str) -> Dict[str, Any]:
        """
        生成周报告
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 周报告数据
        """
        return self._generate_period_report(user_id, 7, "weekly")
    
    def generate_monthly_report(self, user_id: str) -> Dict[str, Any]:
        """
        生成月报告
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 月报告数据
        """
        return self._generate_period_report(user_id, 30, "monthly")
    
    def _generate_period_report(self, user_id: str, days: int, period_type: str) -> Dict[str, Any]:
        """生成周期性报告"""
        report = {
            'user_id': user_id,
            'period_type': period_type,
            'period_days': days,
            'generated_at': datetime.now().isoformat(),
            'summary': {},
            'emotion_trajectory': {},
            'memory_distribution': {},
            'persona_interactions': {},
            'pad_trends': {},
            'visualizations': {}
        }
        
        # 获取数据
        memories = self.ris_model.get_memory_events(user_id, limit=1000)
        interactions = self.ris_model.get_interaction_logs(user_id, limit=1000)
        personas = self.ris_model.get_personas(user_id)
        
        # 过滤时间范围
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_memories = self._filter_by_date(memories, cutoff_date, 'created_at')
        filtered_interactions = self._filter_by_date(interactions, cutoff_date, 'timestamp')
        
        # 生成摘要
        report['summary'] = self._generate_summary(filtered_memories, filtered_interactions, personas)
        
        # 情绪轨迹分析
        report['emotion_trajectory'] = self._analyze_emotion_trajectory(filtered_interactions)
        
        # 回忆分布分析
        report['memory_distribution'] = self._analyze_memory_distribution(filtered_memories)
        
        # 角色交互分析
        report['persona_interactions'] = self._analyze_persona_interactions(filtered_memories, personas)
        
        # PAD趋势分析
        report['pad_trends'] = self._analyze_pad_trends(filtered_interactions)
        
        # 生成可视化图表
        report['visualizations'] = self._generate_visualizations(report, user_id, period_type)
        
        return report
    
    def _filter_by_date(self, items: List[Dict], cutoff_date: datetime, date_field: str) -> List[Dict]:
        """按日期过滤数据"""
        filtered = []
        for item in items:
            try:
                item_date = datetime.fromisoformat(item[date_field].replace('Z', '+00:00'))
                if item_date >= cutoff_date:
                    filtered.append(item)
            except:
                continue
        return filtered
    
    def _generate_summary(self, memories: List[Dict], interactions: List[Dict], personas: List[Dict]) -> Dict[str, Any]:
        """生成摘要信息"""
        summary = {
            'total_memories': len(memories),
            'total_interactions': len(interactions),
            'total_personas': len(personas),
            'active_days': 0,
            'avg_daily_interactions': 0,
            'dominant_emotion': 'neutral',
            'most_active_persona': None,
            'key_insights': []
        }
        
        # 计算活跃天数
        if interactions:
            dates = set()
            for interaction in interactions:
                try:
                    date = datetime.fromisoformat(interaction['timestamp'].replace('Z', '+00:00')).date()
                    dates.add(date)
                except:
                    continue
            summary['active_days'] = len(dates)
            
            if summary['active_days'] > 0:
                summary['avg_daily_interactions'] = len(interactions) / summary['active_days']
        
        # 分析主导情绪
        emotion_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for memory in memories:
            memory_type = memory.get('memory_type', 'neutral')
            emotion_counts[memory_type] += 1
        
        if emotion_counts:
            summary['dominant_emotion'] = max(emotion_counts, key=emotion_counts.get)
        
        # 最活跃角色
        persona_mentions = {}
        for memory in memories:
            entities = memory.get('entities', {})
            persons = entities.get('persons', [])
            for person in persons:
                persona_mentions[person] = persona_mentions.get(person, 0) + 1
        
        if persona_mentions:
            summary['most_active_persona'] = max(persona_mentions, key=persona_mentions.get)
        
        # 关键洞察
        insights = []
        if summary['dominant_emotion'] == 'positive':
            insights.append("本期整体情绪偏向积极")
        elif summary['dominant_emotion'] == 'negative':
            insights.append("本期情绪波动较大，需要关注")
        
        if summary['avg_daily_interactions'] > 5:
            insights.append("交互频率较高，生活较为活跃")
        elif summary['avg_daily_interactions'] < 2:
            insights.append("交互频率较低，可能需要更多社交活动")
        
        summary['key_insights'] = insights
        
        return summary
    
    def _analyze_emotion_trajectory(self, interactions: List[Dict]) -> Dict[str, Any]:
        """分析情绪轨迹"""
        if not interactions:
            return {'trend': 'no_data'}
        
        # 按日期分组
        daily_emotions = {}
        for interaction in interactions:
            try:
                date = datetime.fromisoformat(interaction['timestamp'].replace('Z', '+00:00')).date()
                emotion_label = interaction.get('emotion_label', 'neutral')
                
                if date not in daily_emotions:
                    daily_emotions[date] = []
                daily_emotions[date].append(emotion_label)
            except:
                continue
        
        # 计算每日情绪分布
        trajectory = {}
        for date, emotions in daily_emotions.items():
            emotion_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            for emotion in emotions:
                if emotion in ['happy', 'excited', 'content', 'relaxed']:
                    emotion_counts['positive'] += 1
                elif emotion in ['sad', 'angry', 'anxious']:
                    emotion_counts['negative'] += 1
                else:
                    emotion_counts['neutral'] += 1
            
            total = sum(emotion_counts.values())
            if total > 0:
                trajectory[date.isoformat()] = {
                    'positive_ratio': emotion_counts['positive'] / total,
                    'negative_ratio': emotion_counts['negative'] / total,
                    'neutral_ratio': emotion_counts['neutral'] / total,
                    'total_interactions': total
                }
        
        return {
            'daily_trajectory': trajectory,
            'trend_analysis': self._calculate_emotion_trend(trajectory)
        }
    
    def _analyze_memory_distribution(self, memories: List[Dict]) -> Dict[str, Any]:
        """分析回忆分布"""
        distribution = {
            'by_type': {'positive': 0, 'negative': 0, 'neutral': 0},
            'by_importance': {'high': 0, 'medium': 0, 'low': 0},
            'by_tags': {},
            'by_week': {},
            'patterns': {}
        }
        
        for memory in memories:
            # 按类型分布
            memory_type = memory.get('memory_type', 'neutral')
            distribution['by_type'][memory_type] += 1
            
            # 按重要性分布
            importance = memory.get('importance_score', 0.5)
            if importance >= 0.7:
                distribution['by_importance']['high'] += 1
            elif importance >= 0.4:
                distribution['by_importance']['medium'] += 1
            else:
                distribution['by_importance']['low'] += 1
            
            # 按标签分布
            tags = memory.get('tags', [])
            for tag in tags:
                distribution['by_tags'][tag] = distribution['by_tags'].get(tag, 0) + 1
            
            # 按周分布
            try:
                date = datetime.fromisoformat(memory['created_at'].replace('Z', '+00:00'))
                week = date.strftime('%Y-W%U')
                distribution['by_week'][week] = distribution['by_week'].get(week, 0) + 1
            except:
                continue
        
        # 模式分析
        distribution['patterns'] = self._identify_memory_patterns(distribution)
        
        return distribution
    
    def _analyze_persona_interactions(self, memories: List[Dict], personas: List[Dict]) -> Dict[str, Any]:
        """分析角色交互"""
        interactions = {
            'frequency': {},
            'emotion_association': {},
            'interaction_patterns': {},
            'relationship_strength': {}
        }
        
        # 统计每个角色的提及频率
        for memory in memories:
            entities = memory.get('entities', {})
            persons = entities.get('persons', [])
            memory_type = memory.get('memory_type', 'neutral')
            
            for person in persons:
                # 频率统计
                interactions['frequency'][person] = interactions['frequency'].get(person, 0) + 1
                
                # 情感关联
                if person not in interactions['emotion_association']:
                    interactions['emotion_association'][person] = {'positive': 0, 'negative': 0, 'neutral': 0}
                interactions['emotion_association'][person][memory_type] += 1
        
        # 计算关系强度
        for person, freq in interactions['frequency'].items():
            emotion_dist = interactions['emotion_association'].get(person, {})
            total_emotions = sum(emotion_dist.values())
            
            if total_emotions > 0:
                positive_ratio = emotion_dist.get('positive', 0) / total_emotions
                strength = freq * (1 + positive_ratio)  # 频率 × 积极情感加权
                interactions['relationship_strength'][person] = strength
        
        return interactions
    
    def _analyze_pad_trends(self, interactions: List[Dict]) -> Dict[str, Any]:
        """分析PAD趋势"""
        pad_data = []
        
        for interaction in interactions:
            try:
                detected_emotion = interaction.get('detected_emotion', {})
                timestamp = interaction.get('timestamp', '')
                
                if detected_emotion and timestamp:
                    pad_data.append({
                        'timestamp': timestamp,
                        'pleasure': detected_emotion.get('pleasure', 0.5),
                        'arousal': detected_emotion.get('arousal', 0.5),
                        'dominance': detected_emotion.get('dominance', 0.5)
                    })
            except:
                continue
        
        if not pad_data:
            return {'trend': 'no_data'}
        
        # 计算趋势
        trends = {
            'pleasure': self._calculate_dimension_trend([p['pleasure'] for p in pad_data]),
            'arousal': self._calculate_dimension_trend([p['arousal'] for p in pad_data]),
            'dominance': self._calculate_dimension_trend([p['dominance'] for p in pad_data])
        }
        
        # 计算平均值
        averages = {
            'pleasure': np.mean([p['pleasure'] for p in pad_data]),
            'arousal': np.mean([p['arousal'] for p in pad_data]),
            'dominance': np.mean([p['dominance'] for p in pad_data])
        }
        
        return {
            'trends': trends,
            'averages': averages,
            'data_points': len(pad_data),
            'stability': self._calculate_pad_stability(pad_data)
        }
    
    def _generate_visualizations(self, report: Dict, user_id: str, period_type: str) -> Dict[str, str]:
        """生成可视化图表"""
        visualizations = {}
        
        try:
            # 1. 情绪分布饼图
            visualizations['emotion_pie'] = self._create_emotion_pie_chart(report['memory_distribution'])
            
            # 2. PAD趋势图
            visualizations['pad_trends'] = self._create_pad_trends_chart(report['pad_trends'])
            
            # 3. 角色交互频率柱状图
            visualizations['persona_frequency'] = self._create_persona_frequency_chart(report['persona_interactions'])
            
            # 4. 情绪轨迹线图
            visualizations['emotion_trajectory'] = self._create_emotion_trajectory_chart(report['emotion_trajectory'])
            
            # 5. 回忆重要性分布
            visualizations['importance_distribution'] = self._create_importance_distribution_chart(report['memory_distribution'])
            
        except Exception as e:
            print(f"可视化生成错误: {e}")
            visualizations['error'] = str(e)
        
        return visualizations
    
    def _create_emotion_pie_chart(self, memory_distribution: Dict) -> str:
        """创建情绪分布饼图"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            by_type = memory_distribution.get('by_type', {})
            labels = []
            sizes = []
            colors = []
            
            emotion_map = {
                'positive': ('积极回忆', '#4CAF50'),
                'negative': ('消极回忆', '#F44336'),
                'neutral': ('中性回忆', '#9E9E9E')
            }
            
            for emotion_type, count in by_type.items():
                if count > 0:
                    label, color = emotion_map.get(emotion_type, (emotion_type, '#CCCCCC'))
                    labels.append(f'{label}\n({count})')
                    sizes.append(count)
                    colors.append(color)
            
            if sizes:
                ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax.set_title('回忆情感分布', fontsize=14, fontweight='bold')
            else:
                ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('回忆情感分布', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            # 转换为base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            print(f"饼图生成错误: {e}")
            return ""
    
    def _create_pad_trends_chart(self, pad_trends: Dict) -> str:
        """创建PAD趋势图"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            averages = pad_trends.get('averages', {})
            if not averages:
                ax.text(0.5, 0.5, '暂无PAD数据', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('PAD情感维度分析', fontsize=14, fontweight='bold')
                plt.tight_layout()
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                return image_base64
            
            dimensions = ['Pleasure\n(愉悦度)', 'Arousal\n(唤醒度)', 'Dominance\n(支配度)']
            values = [
                averages.get('pleasure', 0.5),
                averages.get('arousal', 0.5),
                averages.get('dominance', 0.5)
            ]
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
            
            bars = ax.bar(dimensions, values, color=colors, alpha=0.7)
            ax.set_ylim(0, 1)
            ax.set_ylabel('数值', fontsize=12)
            ax.set_title('PAD情感维度平均值', fontsize=14, fontweight='bold')
            
            # 添加数值标签
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{value:.2f}', ha='center', va='bottom')
            
            # 添加参考线
            ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='中性线')
            ax.legend()
            
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            print(f"PAD趋势图生成错误: {e}")
            return ""
    
    def _create_persona_frequency_chart(self, persona_interactions: Dict) -> str:
        """创建角色交互频率图"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            frequency = persona_interactions.get('frequency', {})
            if not frequency:
                ax.text(0.5, 0.5, '暂无角色交互数据', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('角色交互频率', fontsize=14, fontweight='bold')
                plt.tight_layout()
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                return image_base64
            
            # 取前10个最频繁的角色
            sorted_personas = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:10]
            names = [item[0] for item in sorted_personas]
            counts = [item[1] for item in sorted_personas]
            
            bars = ax.bar(range(len(names)), counts, color='#66B2FF', alpha=0.7)
            ax.set_xlabel('角色', fontsize=12)
            ax.set_ylabel('交互次数', fontsize=12)
            ax.set_title('角色交互频率排行', fontsize=14, fontweight='bold')
            ax.set_xticks(range(len(names)))
            ax.set_xticklabels(names, rotation=45, ha='right')
            
            # 添加数值标签
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       str(count), ha='center', va='bottom')
            
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            print(f"角色频率图生成错误: {e}")
            return ""
    
    def _create_emotion_trajectory_chart(self, emotion_trajectory: Dict) -> str:
        """创建情绪轨迹图"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            daily_trajectory = emotion_trajectory.get('daily_trajectory', {})
            if not daily_trajectory:
                ax.text(0.5, 0.5, '暂无情绪轨迹数据', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('情绪轨迹变化', fontsize=14, fontweight='bold')
                plt.tight_layout()
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                return image_base64
            
            dates = sorted(daily_trajectory.keys())
            positive_ratios = [daily_trajectory[date]['positive_ratio'] for date in dates]
            negative_ratios = [daily_trajectory[date]['negative_ratio'] for date in dates]
            neutral_ratios = [daily_trajectory[date]['neutral_ratio'] for date in dates]
            
            date_objects = [datetime.fromisoformat(date) for date in dates]
            
            ax.plot(date_objects, positive_ratios, label='积极情绪', color='#4CAF50', marker='o')
            ax.plot(date_objects, negative_ratios, label='消极情绪', color='#F44336', marker='s')
            ax.plot(date_objects, neutral_ratios, label='中性情绪', color='#9E9E9E', marker='^')
            
            ax.set_xlabel('日期', fontsize=12)
            ax.set_ylabel('情绪比例', fontsize=12)
            ax.set_title('每日情绪轨迹变化', fontsize=14, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # 格式化x轴日期
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//7)))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            print(f"情绪轨迹图生成错误: {e}")
            return ""
    
    def _create_importance_distribution_chart(self, memory_distribution: Dict) -> str:
        """创建重要性分布图"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            by_importance = memory_distribution.get('by_importance', {})
            if not by_importance or sum(by_importance.values()) == 0:
                ax.text(0.5, 0.5, '暂无重要性数据', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('回忆重要性分布', fontsize=14, fontweight='bold')
                plt.tight_layout()
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                return image_base64
            
            labels = ['高重要性', '中等重要性', '低重要性']
            values = [by_importance.get('high', 0), by_importance.get('medium', 0), by_importance.get('low', 0)]
            colors = ['#FF6B6B', '#FFD93D', '#6BCF7F']
            
            bars = ax.bar(labels, values, color=colors, alpha=0.7)
            ax.set_ylabel('回忆数量', fontsize=12)
            ax.set_title('回忆重要性分布', fontsize=14, fontweight='bold')
            
            # 添加数值标签
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       str(value), ha='center', va='bottom')
            
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            print(f"重要性分布图生成错误: {e}")
            return ""
    
    def _analyze_memory_patterns(self, memories: List[Dict]) -> Dict[str, Any]:
        """分析回忆模式"""
        patterns = {
            'peak_hours': {},
            'weekly_patterns': {},
            'emotion_triggers': {},
            'content_themes': {}
        }
        
        for memory in memories:
            try:
                # 分析时间模式
                created_at = datetime.fromisoformat(memory['created_at'].replace('Z', '+00:00'))
                hour = created_at.hour
                weekday = created_at.weekday()
                
                patterns['peak_hours'][hour] = patterns['peak_hours'].get(hour, 0) + 1
                patterns['weekly_patterns'][weekday] = patterns['weekly_patterns'].get(weekday, 0) + 1
                
                # 分析情感触发器
                memory_type = memory.get('memory_type', 'neutral')
                entities = memory.get('entities', {})
                for entity_type, entity_list in entities.items():
                    for entity in entity_list:
                        if entity_type not in patterns['emotion_triggers']:
                            patterns['emotion_triggers'][entity_type] = {}
                        if entity not in patterns['emotion_triggers'][entity_type]:
                            patterns['emotion_triggers'][entity_type][entity] = {'positive': 0, 'negative': 0, 'neutral': 0}
                        patterns['emotion_triggers'][entity_type][entity][memory_type] += 1
                
            except Exception as e:
                continue
        
        return patterns
    
    def _calculate_emotion_trend(self, trajectory: Dict) -> Dict[str, Any]:
        """计算情绪趋势"""
        if not trajectory:
            return {'trend': 'no_data'}
        
        dates = sorted(trajectory.keys())
        if len(dates) < 2:
            return {'trend': 'insufficient_data'}
        
        # 计算积极情绪趋势
        positive_values = [trajectory[date]['positive_ratio'] for date in dates]
        positive_trend = np.polyfit(range(len(positive_values)), positive_values, 1)[0]
        
        # 计算消极情绪趋势
        negative_values = [trajectory[date]['negative_ratio'] for date in dates]
        negative_trend = np.polyfit(range(len(negative_values)), negative_values, 1)[0]
        
        return {
            'positive_trend': positive_trend,
            'negative_trend': negative_trend,
            'overall_trend': 'improving' if positive_trend > 0.01 else 'declining' if positive_trend < -0.01 else 'stable',
            'trend_strength': abs(positive_trend)
        }
    
    def _identify_memory_patterns(self, distribution: Dict) -> Dict[str, Any]:
        """识别回忆模式"""
        patterns = {}
        
        # 分析类型分布模式
        by_type = distribution.get('by_type', {})
        total = sum(by_type.values())
        
        if total > 0:
            positive_ratio = by_type.get('positive', 0) / total
            negative_ratio = by_type.get('negative', 0) / total
            
            if positive_ratio > 0.6:
                patterns['emotion_pattern'] = 'predominantly_positive'
            elif negative_ratio > 0.4:
                patterns['emotion_pattern'] = 'concerning_negative'
            else:
                patterns['emotion_pattern'] = 'balanced'
        
        # 分析标签模式
        by_tags = distribution.get('by_tags', {})
        if by_tags:
            top_tags = sorted(by_tags.items(), key=lambda x: x[1], reverse=True)[:3]
            patterns['top_themes'] = [tag for tag, count in top_tags]
        
        return patterns
    
    def _calculate_dimension_trend(self, values: List[float]) -> float:
        """计算维度趋势"""
        if len(values) < 2:
            return 0.0
        return np.polyfit(range(len(values)), values, 1)[0]
    
    def _calculate_pad_stability(self, pad_data: List[Dict]) -> Dict[str, float]:
        """计算PAD稳定性"""
        if not pad_data:
            return {'pleasure': 0, 'arousal': 0, 'dominance': 0}
        
        stability = {}
        for dimension in ['pleasure', 'arousal', 'dominance']:
            values = [p[dimension] for p in pad_data]
            stability[dimension] = 1.0 - np.std(values)  # 标准差越小，稳定性越高
        
        return stability

# 测试代码
if __name__ == "__main__":
    # 创建测试实例
    report_generator = EmotionReportGenerator("test_ris.db")
    
    print("情绪报告生成器测试")
    
    # 这里可以添加测试代码
    print("情绪报告生成器初始化完成")

