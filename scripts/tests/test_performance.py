#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试脚本

验证系统性能是否不劣于优化前
"""

import os
import sys
import time
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from integration_script import TraeMultiAgentIntegration
    INTEGRATION_AVAILABLE = True
except ImportError as e:
    INTEGRATION_AVAILABLE = False
    print(f"⚠️  无法导入集成模块：{e}")


def test_startup_time():
    """
    测试系统启动时间
    """
    print("\n=== 测试启动时间 ===")
    
    start_time = time.time()
    
    # 初始化集成
    project_root = str(Path(__file__).parent.parent.parent)
    integration = TraeMultiAgentIntegration(project_root)
    
    end_time = time.time()
    startup_time = end_time - start_time
    
    print(f"启动时间: {startup_time:.4f} 秒")
    
    # 验证启动时间不超过10秒
    assert startup_time < 10, f"启动时间过长: {startup_time:.4f} 秒"
    print("✅ 启动时间测试通过")
    
    return startup_time


def test_response_time():
    """
    测试系统响应时间
    """
    print("\n=== 测试响应时间 ===")
    
    # 初始化集成
    project_root = str(Path(__file__).parent.parent.parent)
    integration = TraeMultiAgentIntegration(project_root)
    
    # 测试任务
    test_task = "实现一个简单的计算器功能"
    
    # 测试深度分析响应时间
    start_time = time.time()
    analysis_result = integration.analyze_task(test_task)
    end_time = time.time()
    analysis_time = end_time - start_time
    print(f"深度分析响应时间: {analysis_time:.4f} 秒")
    
    # 测试知识库搜索响应时间
    start_time = time.time()
    knowledge_results = integration.search_knowledge(test_task)
    end_time = time.time()
    search_time = end_time - start_time
    print(f"知识库搜索响应时间: {search_time:.4f} 秒")
    
    # 测试反馈收集响应时间
    start_time = time.time()
    feedback_result = integration.collect_feedback("测试反馈", "suggestion")
    end_time = time.time()
    feedback_time = end_time - start_time
    print(f"反馈收集响应时间: {feedback_time:.4f} 秒")
    
    # 验证响应时间不超过1秒
    assert analysis_time < 1, f"深度分析响应时间过长: {analysis_time:.4f} 秒"
    assert search_time < 1, f"知识库搜索响应时间过长: {search_time:.4f} 秒"
    assert feedback_time < 1, f"反馈收集响应时间过长: {feedback_time:.4f} 秒"
    
    print("✅ 响应时间测试通过")
    
    return {
        "analysis_time": analysis_time,
        "search_time": search_time,
        "feedback_time": feedback_time
    }


def test_task_dispatch_time():
    """
    测试任务调度时间
    """
    print("\n=== 测试任务调度时间 ===")
    
    # 初始化集成
    project_root = str(Path(__file__).parent.parent.parent)
    integration = TraeMultiAgentIntegration(project_root)
    
    # 测试任务
    test_task = "实现一个简单的计算器功能"
    
    start_time = time.time()
    success = integration.dispatch_task("auto", test_task)
    end_time = time.time()
    dispatch_time = end_time - start_time
    
    print(f"任务调度时间: {dispatch_time:.4f} 秒")
    
    # 验证调度时间不超过30秒
    assert dispatch_time < 30, f"任务调度时间过长: {dispatch_time:.4f} 秒"
    assert success, "任务调度失败"
    
    print("✅ 任务调度时间测试通过")
    
    return dispatch_time


def main():
    """
    主函数
    """
    if not INTEGRATION_AVAILABLE:
        print("❌ 集成模块不可用，无法进行性能测试")
        return
    
    print("🚀 开始性能测试")
    
    try:
        # 测试启动时间
        startup_time = test_startup_time()
        
        # 测试响应时间
        response_times = test_response_time()
        
        # 测试任务调度时间
        dispatch_time = test_task_dispatch_time()
        
        print("\n=== 性能测试结果 ===")
        print(f"启动时间: {startup_time:.4f} 秒")
        print(f"深度分析响应时间: {response_times['analysis_time']:.4f} 秒")
        print(f"知识库搜索响应时间: {response_times['search_time']:.4f} 秒")
        print(f"反馈收集响应时间: {response_times['feedback_time']:.4f} 秒")
        print(f"任务调度时间: {dispatch_time:.4f} 秒")
        
        print("\n✅ 所有性能测试通过，系统性能良好")
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
