"""
RIS系统测试套件
全面测试所有功能模块
"""

import unittest
import json
import os
import tempfile
import base64
from datetime import datetime
import requests
import time
import threading

# 导入RIS系统模块
from ris_data_model import RISDataModel
# from enhanced_multimedia_recognizer import EnhancedMultimediaRecognizer
from enhanced_persona_sync import EnhancedPersonaSync
from emotion_report_generator import EmotionReportGenerator

class TestRISDataModel(unittest.TestCase):
    """测试RIS数据模型"""
    
    def setUp(self):
        """测试前准备"""
        self.test_db = "test_ris_data.db"
        self.ris_model = RISDataModel(self.test_db)
        self.test_user_id = "test_user_001"
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_create_user_profile(self):
        """测试创建用户档案"""
        user_id = self.ris_model.create_user_profile()
        self.assertIsNotNone(user_id)
        
        # 测试获取用户档案
        profile = self.ris_model.get_user_profile(user_id)
        self.assertIsNotNone(profile)
        self.assertEqual(profile['user_id'], user_id)
    
    def test_log_interaction(self):
        """测试记录交互"""
        # 先创建用户
        user_id = self.ris_model.create_user_profile()
        
        # 记录交互
        log_id = self.ris_model.log_interaction(
            user_id=user_id,
            input_type="topic",
            detected_emotion={"valence": 0.7, "arousal": 0.5, "dominance": 0.6},
            emotion_label="happy"
        )
        
        self.assertIsNotNone(log_id)
        
        # 获取交互日志
        logs = self.ris_model.get_interaction_logs(user_id)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['log_id'], log_id)
    
    def test_create_memory_event(self):
        """测试创建记忆事件"""
        # 创建用户和交互
        user_id = self.ris_model.create_user_profile()
        log_id = self.ris_model.log_interaction(
            user_id=user_id,
            input_type="topic",
            detected_emotion={"valence": 0.7, "arousal": 0.5, "dominance": 0.6},
            emotion_label="happy"
        )
        
        # 创建记忆事件
        memory_id = self.ris_model.create_memory_event(
            user_id=user_id,
            interaction_log_id=log_id,
            emotion_annotation={"sentiment": "positive", "intensity": 0.8},
            memory_type="positive"
        )
        
        self.assertIsNotNone(memory_id)
        
        # 获取记忆事件
        memories = self.ris_model.get_memory_events(user_id)
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0]['memory_id'], memory_id)
    
    def test_create_persona(self):
        """测试创建角色"""
        user_id = self.ris_model.create_user_profile()
        
        persona_id = self.ris_model.create_persona(
            user_id=user_id,
            name="测试角色",
            personality_traits=["友善", "耐心"]
        )
        
        self.assertIsNotNone(persona_id)
        
        # 获取角色
        personas = self.ris_model.get_personas(user_id)
        self.assertEqual(len(personas), 1)
        self.assertEqual(personas[0]['persona_id'], persona_id)
        self.assertEqual(personas[0]['name'], "测试角色")

class TestEnhancedPersonaSync(unittest.TestCase):
    """测试增强角色同步系统"""
    
    def setUp(self):
        """测试前准备"""
        self.test_db = "test_persona_sync.db"
        self.persona_sync = EnhancedPersonaSync(self.test_db)
        self.test_user_id = "test_user_002"
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_ensure_default_persona(self):
        """测试确保默认角色"""
        persona_id = self.persona_sync.ensure_default_persona(self.test_user_id)
        self.assertIsNotNone(persona_id)
        
        # 再次调用应该返回相同的角色ID
        persona_id2 = self.persona_sync.ensure_default_persona(self.test_user_id)
        self.assertEqual(persona_id, persona_id2)
    
    def test_process_interaction(self):
        """测试处理交互"""
        text = "今天和张三一起去北京出差，心情很好！"
        
        result = self.persona_sync.process_interaction(
            user_id=self.test_user_id,
            text=text,
            input_type="topic"
        )
        
        self.assertIn('interaction_log_id', result)
        self.assertIn('entities', result)
        self.assertIn('pad_analysis', result)
        
        # 检查是否识别出人名
        entities = result['entities']
        self.assertIn('persons', entities)

class TestEmotionReportGenerator(unittest.TestCase):
    """测试情绪报告生成器"""
    
    def setUp(self):
        """测试前准备"""
        self.test_db = "test_report_generator.db"
        self.report_generator = EmotionReportGenerator(self.test_db)
        self.test_user_id = "test_user_003"
        
        # 创建测试数据
        self.ris_model = RISDataModel(self.test_db)
        self.ris_model.create_user_profile(self.test_user_id)
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_classify_memories_by_emotion(self):
        """测试回忆情感分类"""
        # 创建测试记忆
        log_id = self.ris_model.log_interaction(
            user_id=self.test_user_id,
            input_type="topic",
            detected_emotion={"valence": 0.7, "arousal": 0.5, "dominance": 0.6},
            emotion_label="happy"
        )
        
        self.ris_model.create_memory_event(
            user_id=self.test_user_id,
            interaction_log_id=log_id,
            emotion_annotation={"sentiment": "positive"},
            memory_type="positive"
        )
        
        # 测试分类
        classification = self.report_generator.classify_memories_by_emotion(self.test_user_id)
        
        self.assertIn('positive', classification)
        self.assertIn('statistics', classification)
        self.assertEqual(classification['statistics']['positive_count'], 1)
    
    def test_generate_weekly_report(self):
        """测试生成周报告"""
        report = self.report_generator.generate_weekly_report(self.test_user_id)
        
        self.assertIn('period_type', report)
        self.assertEqual(report['period_type'], 'weekly')
        self.assertIn('summary', report)
        self.assertIn('emotion_trajectory', report)

class TestRISSystemIntegration(unittest.TestCase):
    """RIS系统集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.test_db = "test_integration.db"
        self.test_user_id = "integration_test_user"
        
        # 初始化所有组件
        self.ris_model = RISDataModel(self.test_db)
        # self.multimedia_recognizer = EnhancedMultimediaRecognizer()
        self.persona_sync = EnhancedPersonaSync(self.test_db)
        self.report_generator = EmotionReportGenerator(self.test_db)
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_complete_workflow(self):
        """测试完整工作流程"""
        # 1. 创建用户
        user_id = self.ris_model.create_user_profile(self.test_user_id)
        self.assertEqual(user_id, self.test_user_id)
        
        # 2. 处理交互
        text = "今天和小明一起看电影，非常开心！"
        result = self.persona_sync.process_interaction(
            user_id=user_id,
            text=text,
            input_type="topic"
        )
        
        self.assertTrue(result['interaction_log_id'])
        
        # 3. 检查生成的角色
        personas = self.ris_model.get_personas(user_id)
        self.assertGreater(len(personas), 0)  # 至少有默认角色
        
        # 4. 检查生成的记忆
        memories = self.ris_model.get_memory_events(user_id)
        self.assertGreater(len(memories), 0)
        
        # 5. 生成报告
        report = self.report_generator.generate_weekly_report(user_id)
        self.assertIn('summary', report)
        
        # 6. 获取统计信息
        stats = self.ris_model.get_statistics(user_id)
        self.assertGreater(stats['interaction_count'], 0)
        self.assertGreater(stats['memory_count'], 0)

class TestRISAPI(unittest.TestCase):
    """测试RIS API"""
    
    @classmethod
    def setUpClass(cls):
        """启动测试服务器"""
        # 这里可以启动测试服务器
        # 由于在测试环境中，我们跳过实际的API测试
        cls.base_url = "http://localhost:5000"
        cls.skip_api_tests = True  # 在实际部署时设为False
    
    def test_health_endpoint(self):
        """测试健康检查端点"""
        if self.skip_api_tests:
            self.skipTest("跳过API测试")
        
        try:
            response = requests.get(f"{self.base_url}/health")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data['status'], 'healthy')
        except requests.exceptions.ConnectionError:
            self.skipTest("服务器未运行")

def run_all_tests():
    """运行所有测试"""
    print("开始运行RIS系统测试套件...")
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestRISDataModel,
        TestEnhancedPersonaSync,
        TestEmotionReportGenerator,
        TestRISSystemIntegration,
        TestRISAPI
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果
    print(f"\n测试完成:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print("\n✅ 所有测试通过！RIS系统功能正常。")
    else:
        print("\n❌ 部分测试失败，请检查系统功能。")
    
    exit(0 if success else 1)

