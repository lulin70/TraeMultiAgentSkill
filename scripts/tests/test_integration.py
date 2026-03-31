#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TraeMultiAgentSkill 集成测试

验证所有优化模块的协同工作，包括：
- 深度分析能力
- 自动化验证机制
- 专业领域知识库
- 用户体验优化
- 整体集成功能
"""

import os
import sys
import unittest
from pathlib import Path
from datetime import datetime

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入集成模块
try:
    from integration_script import TraeMultiAgentIntegration
    INTEGRATION_AVAILABLE = True
except ImportError as e:
    INTEGRATION_AVAILABLE = False
    print(f"⚠️  无法导入集成模块：{e}")


class TestIntegration(unittest.TestCase):
    """
    集成测试类
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        if not INTEGRATION_AVAILABLE:
            self.skipTest("集成模块不可用")
        
        # 使用当前目录作为测试项目根目录
        self.project_root = str(Path(__file__).parent.parent.parent)
        self.integration = TraeMultiAgentIntegration(self.project_root)
        self.test_task = "实现一个简单的计算器功能"
    
    def test_deep_analysis(self):
        """
        测试深度分析能力
        """
        print("\n=== 测试深度分析能力 ===")
        
        # 测试任务分析
        analysis_result = self.integration.analyze_task(self.test_task)
        
        # 验证分析结果
        self.assertIsInstance(analysis_result, dict)
        self.assertIn("task", analysis_result)
        self.assertIn("analysis", analysis_result)
        self.assertIn("analysis_id", analysis_result)
        self.assertIn("recommendations", analysis_result)
        
        print(f"✅ 深度分析测试通过，分析ID: {analysis_result['analysis_id']}")
    
    def test_automated_testing(self):
        """
        测试自动化验证机制
        """
        print("\n=== 测试自动化验证机制 ===")
        
        # 测试测试用例生成
        test_results = self.integration.generate_tests(self.test_task)
        
        # 验证测试结果
        self.assertIsInstance(test_results, dict)
        self.assertIn("task", test_results)
        self.assertIn("tests_generated", test_results)
        self.assertIn("tests_passed", test_results)
        self.assertIn("pass_rate", test_results)
        self.assertIn("coverage", test_results)
        
        print(f"✅ 自动化测试生成测试通过，生成测试数: {test_results['tests_generated']}")
    
    def test_knowledge_base(self):
        """
        测试专业领域知识库
        """
        print("\n=== 测试专业领域知识库 ===")
        
        # 测试知识库搜索
        search_results = self.integration.search_knowledge("计算器功能")
        
        # 验证搜索结果
        self.assertIsInstance(search_results, list)
        
        print(f"✅ 知识库搜索测试通过，找到结果数: {len(search_results)}")
    
    def test_user_experience(self):
        """
        测试用户体验优化
        """
        print("\n=== 测试用户体验优化 ===")
        
        # 测试反馈收集
        feedback = "这个功能很有用，希望能增加更多计算类型"
        feedback_result = self.integration.collect_feedback(feedback, "suggestion")
        
        # 验证反馈结果
        self.assertIsInstance(feedback_result, dict)
        self.assertIn("feedback", feedback_result)
        self.assertIn("type", feedback_result)
        self.assertIn("feedback_id", feedback_result)
        self.assertIn("analysis", feedback_result)
        
        print(f"✅ 用户体验测试通过，反馈ID: {feedback_result['feedback_id']}")
    
    def test_full_integration(self):
        """
        测试完整的集成功能
        """
        print("\n=== 测试完整集成功能 ===")
        
        # 测试完整的任务调度
        try:
            success = self.integration.dispatch_task("auto", self.test_task)
            print(f"调度结果: {success}")
            # 验证调度结果
            self.assertTrue(success)
            print("✅ 完整集成测试通过")
        except Exception as e:
            print(f"测试失败，错误信息: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def test_error_handling(self):
        """
        测试错误处理
        """
        print("\n=== 测试错误处理 ===")
        
        # 测试空任务
        success = self.integration.dispatch_task("auto", "")
        
        # 验证错误处理
        # 注意：这里可能会成功，因为集成脚本会处理空任务
        # 我们主要测试不会崩溃
        self.assertIsInstance(success, bool)
        
        print("✅ 错误处理测试通过")


if __name__ == '__main__':
    print("🚀 开始 TraeMultiAgentSkill 集成测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试项目根目录: {Path(__file__).parent.parent.parent}")
    
    # 运行测试
    unittest.main(verbosity=2)
