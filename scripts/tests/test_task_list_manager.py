#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TaskListManager 测试用例

测试 TaskListManager 的核心功能：
1. 任务清单创建和加载
2. 任务添加和状态更新
3. 依赖关系管理
4. 优先级排序
5. Markdown 导出
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from task_list_manager import (
    TaskListManager, TaskList, TaskItem,
    TaskStatus, TaskPriority
)


class TestTaskListManager(unittest.TestCase):
    """TaskListManager 测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.manager = TaskListManager(self.test_dir)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_create_tasklist(self):
        """测试创建任务清单"""
        tasklist = self.manager.create_tasklist(
            name="测试任务清单",
            description="这是一个测试任务清单",
            created_by="test_user"
        )
        
        self.assertIsNotNone(tasklist)
        self.assertEqual(tasklist.name, "测试任务清单")
        self.assertEqual(tasklist.status, "active")
        self.assertTrue(tasklist.tasklist_id.startswith("tl_"))
    
    def test_save_and_load_tasklist(self):
        """测试任务清单保存和加载"""
        # 创建
        tasklist = self.manager.create_tasklist(
            name="保存测试",
            created_by="test"
        )
        tasklist_id = tasklist.tasklist_id
        
        # 加载
        loaded = self.manager.load_tasklist(tasklist_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.name, "保存测试")
    
    def test_add_task(self):
        """测试添加任务"""
        tasklist = self.manager.create_tasklist(name="添加任务测试")
        
        task = self.manager.add_task(
            tasklist_id=tasklist.tasklist_id,
            title="测试任务",
            description="任务描述",
            priority=TaskPriority.HIGH,
            assigned_agent="solo-coder",
            estimated_hours=8.0,
            tags=["测试", "开发"],
            category="开发"
        )
        
        self.assertIsNotNone(task)
        self.assertEqual(task.title, "测试任务")
        self.assertEqual(task.priority, TaskPriority.HIGH)
        self.assertEqual(task.estimated_hours, 8.0)
        
        # 验证任务清单中的任务数
        loaded = self.manager.load_tasklist(tasklist.tasklist_id)
        self.assertEqual(len(loaded.tasks), 1)
    
    def test_update_task_status(self):
        """测试更新任务状态"""
        tasklist = self.manager.create_tasklist(name="状态更新测试")
        
        task = self.manager.add_task(
            tasklist_id=tasklist.tasklist_id,
            title="待更新任务",
            priority=TaskPriority.MEDIUM
        )
        
        # 更新状态
        result = self.manager.update_task_status(
            tasklist.tasklist_id,
            task.task_id,
            TaskStatus.IN_PROGRESS
        )
        
        self.assertTrue(result)
        
        # 验证
        loaded = self.manager.load_tasklist(tasklist.tasklist_id)
        updated_task = loaded.tasks[0]
        self.assertEqual(updated_task.status, TaskStatus.IN_PROGRESS)
        self.assertIsNotNone(updated_task.started_at)
    
    def test_task_dependencies(self):
        """测试任务依赖关系"""
        tasklist = self.manager.create_tasklist(name="依赖测试")
        
        # 添加任务1
        task1 = self.manager.add_task(
            tasklist_id=tasklist.tasklist_id,
            title="任务1",
            priority=TaskPriority.HIGH
        )
        
        # 添加任务2，依赖任务1
        task2 = self.manager.add_task(
            tasklist_id=tasklist.tasklist_id,
            title="任务2",
            priority=TaskPriority.MEDIUM,
            depends_on=[task1.task_id]
        )
        
        # 验证依赖
        self.assertEqual(len(task2.depends_on), 1)
        self.assertEqual(task2.depends_on[0], task1.task_id)
    
    def test_is_ready_with_dependencies(self):
        """测试依赖就绪检查"""
        tasklist = self.manager.create_tasklist(name="就绪检查测试")
        
        # 添加任务1
        task1 = self.manager.add_task(
            tasklist_id=tasklist.tasklist_id,
            title="任务1",
            priority=TaskPriority.HIGH
        )
        
        # 添加任务2，依赖任务1
        task2 = self.manager.add_task(
            tasklist_id=tasklist.tasklist_id,
            title="任务2",
            priority=TaskPriority.MEDIUM,
            depends_on=[task1.task_id]
        )
        
        # 任务2 初始不应该就绪
        loaded = self.manager.load_tasklist(tasklist.tasklist_id)
        self.assertFalse(task2.is_ready({t.task_id: t for t in loaded.tasks}))
        
        # 完成任务1
        self.manager.update_task_status(
            tasklist.tasklist_id,
            task1.task_id,
            TaskStatus.COMPLETED
        )
        
        # 重新加载，任务2 应该就绪
        loaded = self.manager.load_tasklist(tasklist.tasklist_id)
        task2_updated = None
        for t in loaded.tasks:
            if t.task_id == task2.task_id:
                task2_updated = t
                break
        
        self.assertIsNotNone(task2_updated)
        self.assertTrue(task2_updated.is_ready({t.task_id: t for t in loaded.tasks}))
    
    def test_get_next_task(self):
        """测试获取下一个可执行任务"""
        tasklist = self.manager.create_tasklist(name="下一个任务测试")
        
        # 添加多个任务
        task1 = self.manager.add_task(
            tasklist_id=tasklist.tasklist_id,
            title="高优先级任务",
            priority=TaskPriority.HIGH,
            assigned_agent="dev1"
        )
        
        task2 = self.manager.add_task(
            tasklist_id=tasklist.tasklist_id,
            title="低优先级任务",
            priority=TaskPriority.LOW,
            assigned_agent="dev2"
        )
        
        # 获取下一个任务（应该是高优先级的）
        next_task = self.manager.get_next_task(tasklist.tasklist_id)
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.task_id, task1.task_id)
        
        # 按 Agent 过滤
        next_task_for_dev2 = self.manager.get_next_task(
            tasklist.tasklist_id,
            agent_id="dev2"
        )
        self.assertIsNotNone(next_task_for_dev2)
        self.assertEqual(next_task_for_dev2.task_id, task2.task_id)
    
    def test_export_to_markdown(self):
        """测试导出为 Markdown"""
        tasklist = self.manager.create_tasklist(
            name="Markdown 导出测试",
            description="测试导出功能"
        )
        
        self.manager.add_task(
            tasklist_id=tasklist.tasklist_id,
            title="待处理任务",
            priority=TaskPriority.MEDIUM,
            category="测试"
        )
        
        self.manager.add_task(
            tasklist_id=tasklist.tasklist_id,
            title="已完成任务",
            priority=TaskPriority.HIGH
        )
        
        # 更新第二个任务为已完成
        loaded = self.manager.load_tasklist(tasklist.tasklist_id)
        if len(loaded.tasks) >= 2:
            # 先设置为进行中，然后再设置为已完成，这样就有状态转换
            self.manager.update_task_status(
                tasklist.tasklist_id,
                loaded.tasks[1].task_id,
                TaskStatus.IN_PROGRESS
            )
            self.manager.update_task_status(
                tasklist.tasklist_id,
                loaded.tasks[1].task_id,
                TaskStatus.COMPLETED
            )
        
        # 导出
        md = self.manager.export_to_markdown(tasklist.tasklist_id)
        
        self.assertIn("Markdown 导出测试", md)
        self.assertIn("待处理任务", md)
        self.assertIn("已完成任务", md)
        self.assertIn("待处理", md)
        self.assertIn("已完成", md)
    
    def test_progress_calculation(self):
        """测试进度计算"""
        tasklist = self.manager.create_tasklist(name="进度测试")
        
        # 添加3个任务
        for i in range(3):
            self.manager.add_task(
                tasklist_id=tasklist.tasklist_id,
                title=f"任务 {i+1}",
                priority=TaskPriority.MEDIUM,
                estimated_hours=10.0
            )
        
        # 完成1个任务
        loaded = self.manager.load_tasklist(tasklist.tasklist_id)
        self.manager.update_task_status(
            tasklist.tasklist_id,
            loaded.tasks[0].task_id,
            TaskStatus.COMPLETED
        )
        
        # 验证进度
        loaded = self.manager.load_tasklist(tasklist.tasklist_id)
        progress = loaded.get_progress()
        self.assertAlmostEqual(progress, 33.33, places=1)


if __name__ == '__main__':
    print("=" * 60)
    print("运行 TaskListManager 单元测试")
    print("=" * 60)
    
    unittest.main(verbosity=2)