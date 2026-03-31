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
from automated_test_generator import AutomatedTestRunner


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
    
    # 使用自动化测试运行器
    runner = AutomatedTestRunner()
    
    # 运行所有测试
    test_report = runner.run_all_tests()
    
    # 打印总结
    print()
    print("=" * 70)
    print("📊 测试结果总结")
    print("=" * 70)
    print(f"总测试数: {test_report['total_tests']}")
    print(f"成功: {test_report['passed_tests']}")
    print(f"失败: {test_report['failed_tests']}")
    print(f"错误: {test_report['error_tests']}")
    
    # 生成测试覆盖率报告
    print()
    print("=" * 70)
    print("📈 测试覆盖率报告")
    print("=" * 70)
    coverage_report = runner.generate_test_coverage_report()
    print(f"整体覆盖率: {coverage_report['overall_coverage']:.1f}%")
    print("模块覆盖率:")
    for module, coverage in coverage_report['module_coverage'].items():
        print(f"- {module}: {coverage:.1f}%")
    print(f"总结: {coverage_report['summary']}")
    
    if test_report['success']:
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
        if test_report['failures']:
            print()
            print("失败详情:")
            for test in test_report['failures']:
                print(f"  - {test}")
        if test_report['errors']:
            print()
            print("错误详情:")
            for test in test_report['errors']:
                print(f"  - {test}")
    
    return test_report['success']


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)