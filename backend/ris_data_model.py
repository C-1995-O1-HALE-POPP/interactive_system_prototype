"""
RIS系统数据模型
实现NoSQL数据结构，支持UserProfile、InteractionLog、MemoryEvent
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import sqlite3
import os

class RISDataModel:
    """RIS系统数据模型类"""
    
    def __init__(self, db_path: str = "ris_system.db"):
        """
        初始化RIS数据模型
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建UserProfile表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                emotion_baseline TEXT,  -- JSON格式存储PAD值
                memory_tags TEXT,       -- JSON格式存储标签数组
                avatar_role TEXT,       -- JSON格式存储角色数组
                created_at TEXT,
                updated_at TEXT,
                metadata TEXT           -- JSON格式存储其他元数据
            )
        ''')
        
        # 创建InteractionLog表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interaction_logs (
                log_id TEXT PRIMARY KEY,
                user_id TEXT,
                timestamp TEXT,
                input_type TEXT,        -- photo, topic, voice
                detected_emotion TEXT,  -- JSON格式存储valence, arousal, dominance
                emotion_label TEXT,     -- sad, calm, happy等
                response_avatar TEXT,
                raw_input_data TEXT,    -- JSON格式存储原始输入数据
                processing_metadata TEXT, -- JSON格式存储处理元数据
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        # 创建MemoryEvent表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_events (
                memory_id TEXT PRIMARY KEY,
                user_id TEXT,
                interaction_log_id TEXT,
                media_reference TEXT,   -- 媒体文件引用
                emotion_annotation TEXT, -- JSON格式存储情感标注
                linked_topic TEXT,      -- 关联话题
                response_history TEXT,  -- JSON格式存储响应历史
                memory_type TEXT,       -- positive, negative, neutral
                importance_score REAL,  -- 重要性评分
                created_at TEXT,
                tags TEXT,              -- JSON格式存储标签
                entities TEXT,          -- JSON格式存储实体信息
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id),
                FOREIGN KEY (interaction_log_id) REFERENCES interaction_logs (log_id)
            )
        ''')
        
        # 创建Personas表（角色表）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personas (
                persona_id TEXT PRIMARY KEY,
                user_id TEXT,
                name TEXT,
                description TEXT,
                personality_traits TEXT, -- JSON格式
                communication_style TEXT,
                emotional_tendencies TEXT, -- JSON格式
                interaction_count INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT,
                context_info TEXT,      -- JSON格式存储上下文信息
                avatar_type TEXT,       -- daughter, friend, etc.
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        # 创建EmotionAnalysis表（情感分析结果）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emotion_analysis (
                analysis_id TEXT PRIMARY KEY,
                interaction_log_id TEXT,
                pad_values TEXT,        -- JSON格式存储Pleasure, Arousal, Dominance
                emotion_categories TEXT, -- JSON格式存储情感分类
                confidence_scores TEXT, -- JSON格式存储置信度
                analysis_method TEXT,   -- 分析方法
                created_at TEXT,
                FOREIGN KEY (interaction_log_id) REFERENCES interaction_logs (log_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"RIS数据库初始化完成: {self.db_path}")
    
    def create_user_profile(self, user_id: str = None, emotion_baseline: Dict = None, 
                          memory_tags: List[str] = None, avatar_role: List[str] = None) -> str:
        """
        创建用户档案
        
        Args:
            user_id: 用户ID，如果为None则自动生成
            emotion_baseline: PAD情感基线
            memory_tags: 记忆标签
            avatar_role: 头像角色
            
        Returns:
            str: 用户ID
        """
        if user_id is None:
            user_id = str(uuid.uuid4())
        
        if emotion_baseline is None:
            emotion_baseline = {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}
        
        if memory_tags is None:
            memory_tags = ["positive", "negative", "neutral"]
        
        if avatar_role is None:
            avatar_role = ["friend"]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_profiles 
            (user_id, emotion_baseline, memory_tags, avatar_role, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            json.dumps(emotion_baseline),
            json.dumps(memory_tags),
            json.dumps(avatar_role),
            now,
            now,
            json.dumps({})
        ))
        
        conn.commit()
        conn.close()
        
        return user_id
    
    def log_interaction(self, user_id: str, input_type: str, detected_emotion: Dict,
                       emotion_label: str, response_avatar: str = None,
                       raw_input_data: Dict = None) -> str:
        """
        记录交互日志
        
        Args:
            user_id: 用户ID
            input_type: 输入类型 (photo, topic, voice)
            detected_emotion: 检测到的情感 (valence, arousal, dominance)
            emotion_label: 情感标签
            response_avatar: 响应头像
            raw_input_data: 原始输入数据
            
        Returns:
            str: 交互日志ID
        """
        log_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interaction_logs 
            (log_id, user_id, timestamp, input_type, detected_emotion, emotion_label, 
             response_avatar, raw_input_data, processing_metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            log_id,
            user_id,
            datetime.now().isoformat(),
            input_type,
            json.dumps(detected_emotion),
            emotion_label,
            response_avatar or "",
            json.dumps(raw_input_data or {}),
            json.dumps({})
        ))
        
        conn.commit()
        conn.close()
        
        return log_id
    
    def create_memory_event(self, user_id: str, interaction_log_id: str,
                          emotion_annotation: Dict, linked_topic: str = None,
                          memory_type: str = "neutral", importance_score: float = 0.5,
                          media_reference: str = None, tags: List[str] = None,
                          entities: Dict = None) -> str:
        """
        创建记忆事件
        
        Args:
            user_id: 用户ID
            interaction_log_id: 交互日志ID
            emotion_annotation: 情感标注
            linked_topic: 关联话题
            memory_type: 记忆类型 (positive, negative, neutral)
            importance_score: 重要性评分
            media_reference: 媒体引用
            tags: 标签
            entities: 实体信息
            
        Returns:
            str: 记忆事件ID
        """
        memory_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO memory_events 
            (memory_id, user_id, interaction_log_id, media_reference, emotion_annotation,
             linked_topic, response_history, memory_type, importance_score, created_at,
             tags, entities)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory_id,
            user_id,
            interaction_log_id,
            media_reference or "",
            json.dumps(emotion_annotation),
            linked_topic or "",
            json.dumps([]),
            memory_type,
            importance_score,
            datetime.now().isoformat(),
            json.dumps(tags or []),
            json.dumps(entities or {})
        ))
        
        conn.commit()
        conn.close()
        
        return memory_id
    
    def create_persona(self, user_id: str, name: str, description: str = None,
                      personality_traits: List[str] = None, communication_style: str = None,
                      avatar_type: str = "friend") -> str:
        """
        创建角色
        
        Args:
            user_id: 用户ID
            name: 角色名称
            description: 角色描述
            personality_traits: 性格特征
            communication_style: 交流风格
            avatar_type: 头像类型
            
        Returns:
            str: 角色ID
        """
        persona_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO personas 
            (persona_id, user_id, name, description, personality_traits, communication_style,
             emotional_tendencies, interaction_count, created_at, updated_at, context_info, avatar_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            persona_id,
            user_id,
            name,
            description or f"角色: {name}",
            json.dumps(personality_traits or []),
            communication_style or "neutral",
            json.dumps({"positive": 0.33, "negative": 0.33, "neutral": 0.34}),
            0,
            now,
            now,
            json.dumps({}),
            avatar_type
        ))
        
        conn.commit()
        conn.close()
        
        return persona_id
    
    def save_emotion_analysis(self, interaction_log_id: str, pad_values: Dict,
                            emotion_categories: Dict, confidence_scores: Dict,
                            analysis_method: str = "multimodal") -> str:
        """
        保存情感分析结果
        
        Args:
            interaction_log_id: 交互日志ID
            pad_values: PAD值
            emotion_categories: 情感分类
            confidence_scores: 置信度
            analysis_method: 分析方法
            
        Returns:
            str: 分析ID
        """
        analysis_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO emotion_analysis 
            (analysis_id, interaction_log_id, pad_values, emotion_categories,
             confidence_scores, analysis_method, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id,
            interaction_log_id,
            json.dumps(pad_values),
            json.dumps(emotion_categories),
            json.dumps(confidence_scores),
            analysis_method,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return analysis_id
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """获取用户档案"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                'user_id': row[0],
                'emotion_baseline': json.loads(row[1]),
                'memory_tags': json.loads(row[2]),
                'avatar_role': json.loads(row[3]),
                'created_at': row[4],
                'updated_at': row[5],
                'metadata': json.loads(row[6])
            }
        return None
    
    def get_interaction_logs(self, user_id: str, limit: int = 50) -> List[Dict]:
        """获取交互日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM interaction_logs 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            logs.append({
                'log_id': row[0],
                'user_id': row[1],
                'timestamp': row[2],
                'input_type': row[3],
                'detected_emotion': json.loads(row[4]),
                'emotion_label': row[5],
                'response_avatar': row[6],
                'raw_input_data': json.loads(row[7]),
                'processing_metadata': json.loads(row[8])
            })
        
        return logs
    
    def get_memory_events(self, user_id: str, memory_type: str = None, limit: int = 50) -> List[Dict]:
        """获取记忆事件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if memory_type:
            cursor.execute('''
                SELECT * FROM memory_events 
                WHERE user_id = ? AND memory_type = ?
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, memory_type, limit))
        else:
            cursor.execute('''
                SELECT * FROM memory_events 
                WHERE user_id = ?
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        memories = []
        for row in rows:
            memories.append({
                'memory_id': row[0],
                'user_id': row[1],
                'interaction_log_id': row[2],
                'media_reference': row[3],
                'emotion_annotation': json.loads(row[4]),
                'linked_topic': row[5],
                'response_history': json.loads(row[6]),
                'memory_type': row[7],
                'importance_score': row[8],
                'created_at': row[9],
                'tags': json.loads(row[10]),
                'entities': json.loads(row[11])
            })
        
        return memories
    
    def get_personas(self, user_id: str) -> List[Dict]:
        """获取用户的所有角色"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM personas WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        
        conn.close()
        
        personas = []
        for row in rows:
            personas.append({
                'persona_id': row[0],
                'user_id': row[1],
                'name': row[2],
                'description': row[3],
                'personality_traits': json.loads(row[4]),
                'communication_style': row[5],
                'emotional_tendencies': json.loads(row[6]),
                'interaction_count': row[7],
                'created_at': row[8],
                'updated_at': row[9],
                'context_info': json.loads(row[10]),
                'avatar_type': row[11]
            })
        
        return personas
    
    def get_emotion_analysis(self, interaction_log_id: str) -> Optional[Dict]:
        """获取情感分析结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM emotion_analysis WHERE interaction_log_id = ?', (interaction_log_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                'analysis_id': row[0],
                'interaction_log_id': row[1],
                'pad_values': json.loads(row[2]),
                'emotion_categories': json.loads(row[3]),
                'confidence_scores': json.loads(row[4]),
                'analysis_method': row[5],
                'created_at': row[6]
            }
        return None
    
    def get_statistics(self, user_id: str) -> Dict:
        """获取用户统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取基本统计
        cursor.execute('SELECT COUNT(*) FROM interaction_logs WHERE user_id = ?', (user_id,))
        interaction_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM memory_events WHERE user_id = ?', (user_id,))
        memory_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM personas WHERE user_id = ?', (user_id,))
        persona_count = cursor.fetchone()[0]
        
        # 获取记忆类型分布
        cursor.execute('''
            SELECT memory_type, COUNT(*) 
            FROM memory_events 
            WHERE user_id = ? 
            GROUP BY memory_type
        ''', (user_id,))
        memory_distribution = dict(cursor.fetchall())
        
        # 获取最近7天的交互
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('''
            SELECT COUNT(*) 
            FROM interaction_logs 
            WHERE user_id = ? AND timestamp > ?
        ''', (user_id, week_ago))
        recent_interactions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'user_id': user_id,
            'interaction_count': interaction_count,
            'memory_count': memory_count,
            'persona_count': persona_count,
            'memory_distribution': memory_distribution,
            'recent_interactions': recent_interactions,
            'timestamp': datetime.now().isoformat()
        }

    # ────────────────────────────
    # 写 assistant 回复到 interaction_logs.processing_metadata
    # ────────────────────────────
    def save_assistant_reply(self, log_id: str, reply: str) -> None:
        """把 LLM 生成的回复写入 interaction_logs.processing_metadata.assistant_reply"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE interaction_logs
            SET processing_metadata = json_set(
                COALESCE(processing_metadata, '{}'),
                '$.assistant_reply', ?
            )
            WHERE log_id = ?
            ''',
            (reply, log_id)
        )
        conn.commit()
        conn.close()

    # ────────────────────────────
    # persona 交互计数自增
    # ────────────────────────────
    def increment_persona_interaction(self, persona_id: str, inc: int = 1) -> None:
        """将 personas.interaction_count += inc，并更新时间戳"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE personas
            SET interaction_count = interaction_count + ?,
                updated_at = ?
            WHERE persona_id = ?
            ''',
            (inc, datetime.now().isoformat(), persona_id)
        )
        conn.commit()
        conn.close()

# 测试代码
if __name__ == "__main__":
    # 创建RIS数据模型实例
    ris_model = RISDataModel("test_ris.db")
    
    # 创建测试用户
    user_id = ris_model.create_user_profile()
    print(f"创建用户: {user_id}")
    
    # 记录交互
    log_id = ris_model.log_interaction(
        user_id=user_id,
        input_type="topic",
        detected_emotion={"valence": 0.7, "arousal": 0.5, "dominance": 0.6},
        emotion_label="happy"
    )
    print(f"记录交互: {log_id}")
    
    # 创建记忆事件
    memory_id = ris_model.create_memory_event(
        user_id=user_id,
        interaction_log_id=log_id,
        emotion_annotation={"sentiment": "positive", "intensity": 0.8},
        memory_type="positive"
    )
    print(f"创建记忆: {memory_id}")
    
    # 创建角色
    persona_id = ris_model.create_persona(
        user_id=user_id,
        name="小助手",
        personality_traits=["友善", "耐心"]
    )
    print(f"创建角色: {persona_id}")
    
    # 获取统计信息
    stats = ris_model.get_statistics(user_id)
    print(f"统计信息: {stats}")
    
    # 清理测试数据
    os.remove("test_ris.db")
    print("测试完成")

