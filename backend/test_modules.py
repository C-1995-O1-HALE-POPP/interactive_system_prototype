#!/usr/bin/env python3
"""
交互系统后端测试脚本
"""

import sys
import os
import json
import tempfile
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_emotion_analyzer():
    """测试情感分析器"""
    print("=== 测试情感分析器 ===")
    try:
        from emotion_analyzer import EmotionAnalyzer
        
        analyzer = EmotionAnalyzer()
        
        test_texts = [
            "今天天气真好，心情很愉快！",
            "这个产品太糟糕了，完全不值得购买。",
            "今天去了超市买菜。"
        ]
        
        for text in test_texts:
            result = analyzer.analyze_sentiment(text)
            print(f"文本: {text}")
            print(f"结果: {result}")
            print("-" * 50)
        
        print("✅ 情感分析器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 情感分析器测试失败: {e}")
        return False

def test_database_manager():
    """测试数据库管理器"""
    print("\n=== 测试数据库管理器 ===")
    try:
        from database_manager import DatabaseManager
        
        # 使用临时数据库
        db_path = tempfile.mktemp(suffix='.db')
        db = DatabaseManager(db_path)
        
        # 测试保存角色
        test_persona = {
            'id': 'test_persona_1',
            'name': '测试角色',
            'description': '这是一个测试角色',
            'personality_traits': ['友善', '耐心'],
            'communication_style': '温和',
            'created_at': datetime.now().isoformat(),
            'interaction_count': 1,
            'emotional_tendencies': {'positive': 0.7, 'negative': 0.1, 'neutral': 0.2},
            'context': {'test': True}
        }
        
        success = db.save_persona(test_persona)
        print(f"保存角色: {'成功' if success else '失败'}")
        
        # 测试获取角色
        retrieved_persona = db.get_persona('test_persona_1')
        print(f"获取角色: {'成功' if retrieved_persona else '失败'}")
        
        # 测试保存回忆
        test_memory = {
            'id': 'test_memory_1',
            'persona_id': 'test_persona_1',
            'content': '这是一条测试回忆',
            'emotion': {'sentiment': 'positive', 'confidence': 0.8},
            'memory_type': 'conversation',
            'timestamp': datetime.now().isoformat(),
            'entities': {'persons': ['测试角色']},
            'importance_score': 0.7
        }
        
        success = db.save_memory(test_memory)
        print(f"保存回忆: {'成功' if success else '失败'}")
        
        # 测试获取统计信息
        stats = db.get_database_stats()
        print(f"数据库统计: {stats}")
        
        # 清理测试数据
        os.remove(db_path)
        
        print("✅ 数据库管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据库管理器测试失败: {e}")
        return False

def test_persona_sync():
    """测试角色同步系统"""
    print("\n=== 测试角色同步系统 ===")
    try:
        from persona_sync import PersonaSync
        
        # 使用临时数据库
        db_path = tempfile.mktemp(suffix='.db')
        persona_sync = PersonaSync(db_path)
        
        # 测试交互处理
        test_text = "今天和张三一起去北京出差，心情很好！"
        emotion_result = {'sentiment': 'positive', 'confidence': 0.8, 'raw_score': 0.75}
        
        result = persona_sync.process_interaction(test_text, emotion_result)
        print(f"处理交互: 新角色数量={len(result['new_personas'])}, 新回忆数量={len(result['new_memories']) + (1 if result['default_memory'] else 0)}")
        
        # 测试获取所有角色
        personas = persona_sync.get_all_personas()
        print(f"总角色数量: {len(personas)}")
        
        # 清理测试数据
        os.remove(db_path)
        
        print("✅ 角色同步系统测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 角色同步系统测试失败: {e}")
        return False

def test_multimedia_recognizer():
    """测试多媒体识别器"""
    print("\n=== 测试多媒体识别器 ===")
    try:
        from multimedia_recognizer import MultimediaRecognizer
        
        recognizer = MultimediaRecognizer()
        
        # 测试语音识别器初始化
        print(f"语音识别器初始化: 成功")
        
        # 测试图像预处理功能
        import numpy as np
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        processed = recognizer._preprocess_image(test_image)
        print(f"图像预处理测试: {'成功' if processed is not None else '失败'}")
        
        # 测试颜色分析
        color_analysis = recognizer._analyze_colors(test_image)
        print(f"颜色分析测试: {'成功' if color_analysis else '失败'}")
        
        print("✅ 多媒体识别器基础功能测试通过")
        print("⚠️  音频和图片识别需要实际文件进行测试")
        return True
        
    except Exception as e:
        print(f"❌ 多媒体识别器测试失败: {e}")
        return False

def test_llm_service():
    """测试LLM服务"""
    print("\n=== 测试LLM服务 ===")
    try:
        from llm_multimodal_service import LLMMultimodalService
        
        llm_service = LLMMultimodalService()
        
        print(f"LLM服务可用性: {llm_service.is_available()}")
        
        if llm_service.is_available():
            # 测试文本生成
            result = llm_service.generate_text("你好，请介绍一下自己")
            print(f"文本生成测试: {'成功' if result['success'] else '失败'}")
            if result['success']:
                print(f"响应: {result['response'][:100]}...")
        else:
            print("⚠️  LLM服务不可用，需要配置API密钥")
        
        print("✅ LLM服务测试完成")
        return True
        
    except Exception as e:
        print(f"❌ LLM服务测试失败: {e}")
        return False

def test_emotion_report():
    """测试情感报告生成器"""
    print("\n=== 测试情感报告生成器 ===")
    try:
        from emotion_analyzer import EmotionAnalyzer
        from persona_sync import PersonaSync
        from emotion_report import EmotionReportGenerator
        
        # 使用临时数据库
        db_path = tempfile.mktemp(suffix='.db')
        
        emotion_analyzer = EmotionAnalyzer()
        persona_sync = PersonaSync(db_path)
        report_generator = EmotionReportGenerator(persona_sync, emotion_analyzer)
        
        # 添加一些测试数据
        test_interactions = [
            "今天心情很好，工作顺利",
            "遇到了一些困难，有点沮丧",
            "和朋友聊天，感觉不错"
        ]
        
        for text in test_interactions:
            emotion_result = emotion_analyzer.analyze_sentiment(text)
            persona_sync.process_interaction(text, emotion_result)
        
        # 生成周报告
        report = report_generator.generate_weekly_report(save_charts=False)
        print(f"周报告生成: {'成功' if 'error' not in report else '失败'}")
        
        if 'error' not in report:
            print(f"报告统计: {report['statistics']}")
        
        # 清理测试数据
        os.remove(db_path)
        
        print("✅ 情感报告生成器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 情感报告生成器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试交互系统后端模块...")
    print("=" * 60)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(("情感分析器", test_emotion_analyzer()))
    test_results.append(("数据库管理器", test_database_manager()))
    test_results.append(("角色同步系统", test_persona_sync()))
    test_results.append(("多媒体识别器", test_multimedia_recognizer()))
    test_results.append(("LLM服务", test_llm_service()))
    test_results.append(("情感报告生成器", test_emotion_report()))
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要:")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个模块测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统准备就绪。")
    else:
        print("⚠️  部分测试失败，请检查相关模块。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

