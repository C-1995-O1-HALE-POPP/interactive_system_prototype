"""
RIS系统主应用 - 集成所有功能模块的Flask后端
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import tempfile
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional

# 导入RIS系统模块
from ris_data_model import RISDataModel
# from enhanced_multimedia_recognizer import EnhancedMultimediaRecognizer
from enhanced_persona_sync import EnhancedPersonaSync
from emotion_report_generator import EmotionReportGenerator

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化RIS系统组件
ris_model = RISDataModel("ris_system.db")
# multimedia_recognizer = EnhancedMultimediaRecognizer()
persona_sync = EnhancedPersonaSync("ris_system.db")
report_generator = EmotionReportGenerator("ris_system.db")

print("RIS系统后端启动中...")


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        # 获取系统统计信息
        stats = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'database_connected': True,
                'modules_loaded': [
                    'RISDataModel',
                    'PADEmotionAnalyzer', 
                    'EnhancedMultimediaRecognizer',
                    'EnhancedPersonaSync',
                    'EmotionReportGenerator',
                    'BailianDeepSeekService'
                ],
                'llm_service_status': persona_sync.llm.get_status()
            }
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """创建新用户"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        # 创建用户档案
        created_user_id = ris_model.create_user_profile(
            user_id=user_id,
            emotion_baseline=data.get('emotion_baseline'),
            memory_tags=data.get('memory_tags'),
            avatar_role=data.get('avatar_role')
        )
        
        # 确保默认角色
        persona_sync._ensure_default_persona(created_user_id)
        
        return jsonify({
            'success': True,
            'user_id': created_user_id,
            'message': '用户创建成功'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    """获取用户档案"""
    try:
        profile = ris_model.get_user_profile(user_id)
        if profile:
            # 获取统计信息
            stats = ris_model.get_statistics(user_id)
            profile['statistics'] = stats
            return jsonify({'success': True, 'profile': profile})
        else:
            return jsonify({'success': False, 'error': '用户不存在'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interactions', methods=['POST'])
def process_interaction():
    """处理用户交互"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        text = data.get('text', '')
        input_type = data.get('input_type', 'topic')
        
        if not user_id:
            return jsonify({'success': False, 'error': '缺少用户ID'}), 400
        
        # 确保用户存在
        user_profile = ris_model.get_user_profile(user_id)
        if not user_profile:
            ris_model.create_user_profile(user_id)
        
        # 处理交互
        result = persona_sync.process_interaction(
            user_id=user_id,
            text=text,
            input_type=input_type,
            persona_id=data.get('persona_id', None),
        )
        
        return jsonify({'success': True, 'result': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/image_interactions', methods=['POST'])
def process_image_interaction():
    """处理带图片的用户交互，这里用表单数据接收"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': '没有图像文件'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': '文件名为空'}), 400
        
        # 保存临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        data = request.form
        user_id = data.get('user_id')
        text = data.get('text', '')
        input_type = data.get('input_type', 'topic')
        
        if not user_id:
            return jsonify({'success': False, 'error': '缺少用户ID'}), 400
        
        # 确保用户存在
        user_profile = ris_model.get_user_profile(user_id)
        if not user_profile:
            ris_model.create_user_profile(user_id)
        
        # 处理交互
        result = persona_sync.process_interaction(
            user_id=user_id,
            text=text,
            input_type=input_type,
            image_path=temp_path,  # 使用临时文件路径
            persona_id=data.get('persona_id', None),
        )
        
        return jsonify({'success': True, 'result': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/emotions/pad', methods=['POST'])
def analyze_pad_emotion():
    """PAD情感分析"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'success': False, 'error': '缺少文本内容'}), 400
        
        result = persona_sync._analyze_emotion(text=text)
        return jsonify({'success': True, 'result': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/personas/<user_id>', methods=['GET'])
def get_user_personas(user_id):
    """获取用户的所有角色"""
    try:
        personas = ris_model.get_personas(user_id)
        return jsonify({'success': True, 'personas': personas})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/personas/<user_id>/<persona_id>/insights', methods=['GET'])
def get_persona_insights(user_id, persona_id):
    """获取角色洞察"""
    try:
        # 获取角色数据
        personas = ris_model.get_personas(user_id)
        persona_data = None
        for p in personas:
            if p['persona_id'] == persona_id:
                persona_data = p
                break
        
        if not persona_data:
            return jsonify({'success': False, 'error': '角色不存在'}), 404
        
        # 获取交互历史
        interaction_history = ris_model.get_interaction_logs(user_id, limit=20)
        
        result = persona_sync.generate_persona_insights(
            persona_data=persona_data,
            interaction_history=interaction_history
        )
        
        return jsonify({'success': True, 'result': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memories/<user_id>', methods=['GET'])
def get_user_memories(user_id):
    """获取用户回忆"""
    try:
        memory_type = request.args.get('type')
        limit = int(request.args.get('limit', 50))
        
        memories = ris_model.get_memory_events(user_id, memory_type, limit)
        return jsonify({'success': True, 'memories': memories})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/memories/classify/<user_id>', methods=['GET'])
def classify_memories(user_id):
    """回忆情感分类"""
    try:
        time_range = int(request.args.get('days', 30))
        
        classification = report_generator.classify_memories_by_emotion(user_id, time_range)
        return jsonify({'success': True, 'classification': classification})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/<user_id>/weekly', methods=['GET'])
def generate_weekly_report(user_id):
    """生成周报告"""
    try:
        report = report_generator.generate_weekly_report(user_id)
        return jsonify({'success': True, 'report': report})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/<user_id>/monthly', methods=['GET'])
def generate_monthly_report(user_id):
    """生成月报告"""
    try:
        report = report_generator.generate_monthly_report(user_id)
        return jsonify({'success': True, 'report': report})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interactions/<user_id>', methods=['GET'])
def get_interaction_logs(user_id):
    """获取交互日志"""
    try:
        limit = int(request.args.get('limit', 50))
        
        logs = ris_model.get_interaction_logs(user_id, limit)
        return jsonify({'success': True, 'logs': logs})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/statistics/<user_id>', methods=['GET'])
def get_user_statistics(user_id):
    """获取用户统计信息"""
    try:
        stats = ris_model.get_statistics(user_id)
        return jsonify({'success': True, 'statistics': stats})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/system/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    try:
        info = {
            'system_name': 'RIS (Relationship Intelligence System)',
            'version': '1.0.0',
            'description': '关系智能系统 - 多模态情感分析与角色记忆管理',
            'features': [
                '多模态数据采集（文本、音频、图像）',
                'PAD情感分析',
                '智能角色生成与管理',
                '个性化回忆档案',
                '情绪轨迹报告',
                '可视化图表生成'
            ],
            'api_endpoints': {
                'users': '/api/users',
                'interactions': '/api/interactions',
                'multimedia': '/api/multimedia',
                'emotions': '/api/emotions',
                'personas': '/api/personas',
                'memories': '/api/memories',
                'reports': '/api/reports',
                'statistics': '/api/statistics'
            },
            'timestamp': datetime.now().isoformat()
        }
        return jsonify({'success': True, 'info': info})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'API端点不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    print("RIS系统后端启动完成")
    print("API文档: http://localhost:11451/api/system/info")
    print("健康检查: http://localhost:11451/health")
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=11451, debug=True)

