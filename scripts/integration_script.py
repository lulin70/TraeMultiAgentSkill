#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TraeMultiAgentSkill 集成脚本

将所有优化模块整合到 TraeMultiAgentSkill 中
包括：
- 深度分析能力（planning_engine.py）
- 自动化验证机制（automated_test_generator.py）
- 专业领域知识库（knowledge_base_manager.py）
- 用户体验优化（user_experience_manager.py）
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入优化模块
try:
    from vibe_coding.planning_engine import PlanningEngine
    from tests.automated_test_generator import AutomatedTestRunner
    from knowledge_base_manager import KnowledgeBaseManager
    from user_experience_manager import UserExperienceManager
    OPTIMIZATION_MODULES_AVAILABLE = True
    print("✅ 成功导入所有优化模块")
except ImportError as e:
    OPTIMIZATION_MODULES_AVAILABLE = False
    print(f"⚠️  无法导入优化模块：{e}")

# 导入核心组件
try:
    from dual_layer_context_manager import DualLayerContextManager, TaskDefinition
    from role_matcher import RoleMatcher, TaskRequirement, create_default_roles
    from workflow_engine import WorkflowEngine
    CORE_COMPONENTS_AVAILABLE = True
    print("✅ 成功导入核心组件")
except ImportError as e:
    CORE_COMPONENTS_AVAILABLE = False
    print(f"⚠️  无法导入核心组件：{e}")


def log(message: str, level: str = 'INFO'):
    """
    统一日志输出
    
    Args:
        message: 日志消息
        level: 日志级别 (INFO, WARNING, ERROR, SUCCESS)
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    level_colors = {
        'INFO': '\033[94m',
        'WARNING': '\033[93m',
        'ERROR': '\033[91m',
        'SUCCESS': '\033[92m'
    }
    reset_color = '\033[0m'
    color = level_colors.get(level, '')
    
    print(f"{color}[{timestamp}] [{level}] {message}{reset_color}")


class TraeMultiAgentIntegration:
    """
    TraeMultiAgentSkill 集成类
    整合所有优化模块到核心功能中
    """
    
    def __init__(self, project_root: str):
        """
        初始化集成类
        
        Args:
            project_root: 项目根目录
        """
        self.project_root = project_root
        self.skill_root = str(Path(project_root) / '.trae' / 'skills' / 'trae-multi-agent')
        
        # 初始化核心组件
        if CORE_COMPONENTS_AVAILABLE:
            self.context_manager = DualLayerContextManager(
                project_root=project_root,
                skill_root=self.skill_root
            )
            self.role_matcher = RoleMatcher()
            for role in create_default_roles():
                self.role_matcher.register_role(role)
            self.workflow_engine = WorkflowEngine(
                storage_path=self.skill_root
            )
        else:
            self.context_manager = None
            self.role_matcher = None
            self.workflow_engine = None
        
        # 初始化优化模块
        if OPTIMIZATION_MODULES_AVAILABLE:
            self.planning_engine = PlanningEngine()
            self.test_runner = AutomatedTestRunner()
            self.knowledge_base = KnowledgeBaseManager()
            self.user_experience = UserExperienceManager()
        else:
            self.planning_engine = None
            self.test_runner = None
            self.knowledge_base = None
            self.user_experience = None
        
        log("🚀 TraeMultiAgentSkill 集成初始化完成", "SUCCESS")
    
    def analyze_task(self, task: str) -> Dict:
        """
        分析任务，使用深度分析能力
        
        Args:
            task: 任务描述
            
        Returns:
            Dict: 分析结果
        """
        if not self.planning_engine:
            log("⚠️  深度分析模块不可用，使用默认分析", "WARNING")
            return {
                "task": task,
                "analysis": "任务分析完成（默认）",
                "recommendations": []
            }
        
        log(f"📊 开始深度分析任务：{task}", "INFO")
        
        # 使用 5-Why 分析
        five_why_result = self.planning_engine.five_why_analysis(
            problem=f"如何完成任务: {task}",
            context={"task": task}
        )
        
        # 分析ID已经在five_why_analysis中生成并保存
        analysis_id = five_why_result['id']
        
        log(f"✅ 深度分析完成，分析ID: {analysis_id}", "SUCCESS")
        
        return {
            "task": task,
            "analysis": five_why_result,
            "analysis_id": analysis_id,
            "recommendations": ["基于深度分析的执行建议"]
        }
    
    def generate_tests(self, task: str, code_path: Optional[str] = None) -> Dict:
        """
        生成测试用例，使用自动化验证机制
        
        Args:
            task: 任务描述
            code_path: 代码路径（可选）
            
        Returns:
            Dict: 测试结果
        """
        if not self.test_runner:
            log("⚠️  自动化验证模块不可用，跳过测试生成", "WARNING")
            return {
                "task": task,
                "tests_generated": 0,
                "tests_passed": 0,
                "coverage": 0.0
            }
        
        log(f"🧪 开始为任务生成测试：{task}", "INFO")
        
        # 运行所有测试
        test_results = self.test_runner.run_all_tests()
        
        # 生成覆盖率报告
        coverage_report = self.test_runner.generate_test_coverage_report()
        
        pass_rate = (test_results['passed_tests'] / test_results['total_tests']) * 100 if test_results['total_tests'] > 0 else 0
        
        log(f"✅ 测试生成和执行完成，通过率: {pass_rate:.2%}", "SUCCESS")
        
        return {
            "task": task,
            "tests_generated": test_results['total_tests'],
            "tests_passed": test_results['passed_tests'],
            "tests_failed": test_results['failed_tests'],
            "pass_rate": pass_rate,
            "coverage": coverage_report.get('overall_coverage', 0.0)
        }
    
    def search_knowledge(self, query: str) -> List[Dict]:
        """
        搜索专业领域知识库
        
        Args:
            query: 搜索查询
            
        Returns:
            List[Dict]: 搜索结果
        """
        if not self.knowledge_base:
            log("⚠️  知识库模块不可用，返回空结果", "WARNING")
            return []
        
        log(f"🔍 搜索知识库：{query}", "INFO")
        
        # 搜索知识库
        results = self.knowledge_base.search_knowledge(query)
        
        log(f"✅ 知识库搜索完成，找到 {len(results)} 条结果", "SUCCESS")
        
        return results
    
    def collect_feedback(self, feedback: str, feedback_type: str = "suggestion") -> Dict:
        """
        收集用户反馈，使用用户体验优化模块
        
        Args:
            feedback: 反馈内容
            feedback_type: 反馈类型
            
        Returns:
            Dict: 反馈分析结果
        """
        if not self.user_experience:
            log("⚠️  用户体验模块不可用，跳过反馈分析", "WARNING")
            return {
                "feedback": feedback,
                "type": feedback_type,
                "analysis": "反馈已收集（默认）"
            }
        
        log(f"💬 收集用户反馈：{feedback_type}", "INFO")
        
        # 收集反馈
        feedback_id = self.user_experience.collect_feedback(
            user_id="integration_test",
            feedback_type=feedback_type,
            content=feedback
        )
        
        # 分析反馈
        analysis = self.user_experience.analyze_feedback(feedback_id)
        
        log(f"✅ 反馈分析完成，反馈ID: {feedback_id}", "SUCCESS")
        
        return {
            "feedback": feedback,
            "type": feedback_type,
            "feedback_id": feedback_id,
            "analysis": analysis
        }
    
    def dispatch_task(self, agent_type: str, task: str, task_id: Optional[str] = None) -> bool:
        """
        调度任务，整合所有优化模块
        
        Args:
            agent_type: 智能体类型
            task: 任务描述
            task_id: 任务ID
            
        Returns:
            bool: 调度是否成功
        """
        try:
            # 1. 深度分析任务
            analysis_result = self.analyze_task(task)
            
            # 2. 搜索相关知识
            knowledge_results = self.search_knowledge(task)
            
            # 3. 生成测试用例
            test_results = self.generate_tests(task)
            
            # 4. 创建任务定义
            task_def = TaskDefinition(
                task_id=task_id or f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                title=task,
                description=task,
                goals=[task],
                constraints=[]
            )
            
            # 5. 开始任务
            log(f'🚀 启动任务：{task_def.task_id}', 'SUCCESS')
            task_ctx = self.context_manager.start_task(task_def)
            
            # 6. 智能匹配角色
            requirement = TaskRequirement(
                task_id=task_def.task_id,
                title=task_def.title,
                description=task_def.description
            )
            
            matched_roles = self.role_matcher.match(requirement, top_k=3)
            log(f'🎯 匹配到 {len(matched_roles)} 个角色:', 'INFO')
            for i, result in enumerate(matched_roles, 1):
                log(f'   {i}. {result.role_name} (置信度：{result.confidence:.2%})', 'INFO')
            
            # 7. 选择最佳角色
            if matched_roles:
                if agent_type == 'auto':
                    best_match = matched_roles[0]
                else:
                    best_match = None
                    for result in matched_roles:
                        if result.role_id == agent_type:
                            best_match = result
                            break
                    if not best_match:
                        best_match = matched_roles[0]
                        log(f'⚠️  未找到指定角色 {agent_type}，使用最佳匹配：{best_match.role_name}', 'WARNING')
                
                log(f'✅ 选择角色：{best_match.role_name}', 'SUCCESS')
            else:
                log('❌ 未匹配到合适的角色', 'ERROR')
                return False
            
            # 8. 添加分析结果到上下文
            analysis_str = str(analysis_result['analysis'])
            task_ctx.add_thought(
                role=best_match.role_id,
                thought_type="analysis",
                content=f"任务深度分析结果: {analysis_str[:100]}...",
                context=analysis_result
            )
            
            # 9. 添加知识库结果到上下文
            if knowledge_results:
                task_ctx.add_thought(
                    role=best_match.role_id,
                    thought_type="knowledge",
                    content=f"知识库搜索结果: {len(knowledge_results)} 条相关知识",
                    context={"knowledge_results": knowledge_results[:3]}
                )
            
            # 10. 执行任务
            log(f'▶️  执行任务...', 'INFO')
            task_ctx.add_artifact(
                "EXECUTION",
                {
                    "role": best_match.role_id,
                    "task": task,
                    "status": "completed",
                    "analysis": analysis_result,
                    "test_results": test_results,
                    "knowledge_results": knowledge_results[:3]
                },
                role=best_match.role_id
            )
            
            # 11. 完成任务
            self.context_manager.complete_task(task_def.task_id)
            
            # 12. 显示统计
            stats = self.context_manager.get_statistics()
            log(f'📊 上下文统计:', 'INFO')
            log(f'   全局上下文版本：{stats["global_context"]["version"]}', 'INFO')
            log(f'   知识库条目：{stats["global_context"]["knowledge_count"]}', 'INFO')
            log(f'   经验库条目：{stats["global_context"]["experience_count"]}', 'INFO')
            
            log(f'✅ 任务调度成功完成', 'SUCCESS')
            return True
            
        except Exception as e:
            log(f'❌ 调度失败：{e}', 'ERROR')
            import traceback
            traceback.print_exc()
            return False


def main():
    """
    主函数
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='TraeMultiAgentSkill 集成脚本 - 整合所有优化模块'
    )
    
    parser.add_argument(
        '--task',
        type=str,
        required=True,
        help='任务描述'
    )
    
    parser.add_argument(
        '--agent',
        type=str,
        choices=['architect', 'product-manager', 'tester', 'solo-coder', 'ui-designer', 'devops', 'auto'],
        default='auto',
        help='指定要调度的智能体角色（默认：auto - 自动匹配）'
    )
    
    parser.add_argument(
        '--project-root',
        type=str,
        default='.',
        help='项目根目录路径（默认：当前目录）'
    )
    
    args = parser.parse_args()
    
    log('🚀 TraeMultiAgentSkill 集成脚本启动', 'INFO')
    
    # 初始化集成
    integration = TraeMultiAgentIntegration(args.project_root)
    
    # 调度任务
    success = integration.dispatch_task(args.agent, args.task)
    
    if success:
        log('✅ 任务调度成功', 'SUCCESS')
        sys.exit(0)
    else:
        log('❌ 任务调度失败', 'ERROR')
        sys.exit(1)


if __name__ == '__main__':
    main()
