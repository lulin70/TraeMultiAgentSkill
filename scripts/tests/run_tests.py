#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本

运行所有单元测试和集成测试
"""

import sys
import unittest
from pathlib import Path

# 添加脚本目录到路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# 导入测试模块
from test_checkpoint_manager import TestCheckpointManager, TestHandoffDocument
from test_task_list_manager import TestTaskListManager
from test_workflow_engine_v2 import TestWorkflowEngineV2, TestCheckpointAndHandoffIntegration


def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("🧪 Trae Multi-Agent - 长程 Agent 功能测试套件")
    print("=" * 70)
    print()
    print("基于 Anthropic 《Effective Harnesses for Long-Running Agents》")
    print("核心改进：Checkpoint + Handoff + TaskList")
    print()
    print("=" * 70)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestCheckpointManager))
    suite.addTests(loader.loadTestsFromTestCase(TestHandoffDocument))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskListManager))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowEngineV2))
    suite.addTests(loader.loadTestsFromTestCase(TestCheckpointAndHandoffIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print()
    print("=" * 70)
    print("📊 测试结果总结")
    print("=" * 70)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.wasSuccessful():
        print()
        print("🎉 所有测试通过！")
        print()
        print("✅ CheckpointManager - 检查点保存和恢复功能正常")
        print("✅ HandoffDocument - 交接文档生成功能正常")
        print("✅ TaskListManager - 任务清单管理功能正常")
        print("✅ WorkflowEngineV2 - 增强版工作流引擎功能正常")
        print()
        print("基于 Anthropic 的长程 Agent 改进已成功实现！")
    else:
        print()
        print("❌ 部分测试失败，请检查上述错误信息")
        if result.failures:
            print()
            print("失败详情:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print()
            print("错误详情:")
            for test, traceback in result.errors:
                print(f"  - {test}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)