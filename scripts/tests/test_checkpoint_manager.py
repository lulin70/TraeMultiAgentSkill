#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CheckpointManager 测试用例

测试 CheckpointManager 的核心功能：
1. 检查点保存和加载
2. 数据完整性校验
3. 过期检查点清理
4. 交接文档生成
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from checkpoint_manager import (
    CheckpointManager, Checkpoint, CheckpointStatus,
    HandoffDocument
)


class TestCheckpointManager(unittest.TestCase):
    """CheckpointManager 测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.manager = CheckpointManager(self.test_dir)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_save_and_load_checkpoint(self):
        """测试检查点保存和加载"""
        checkpoint = Checkpoint(
            checkpoint_id="test_cp_001",
            task_id="task_001",
            step_id="step_1",
            step_name="测试步骤",
            agent_id="test_agent",
            status=CheckpointStatus.ACTIVE,
            completed_steps=["step_0"],
            remaining_steps=["step_2", "step_3"],
            progress_percentage=33.3,
            context_snapshot={"key": "value"},
            variables={"var1": "test"}
        )
        
        # 保存
        result = self.manager.save_checkpoint(checkpoint)
        self.assertTrue(result)
        
        # 加载
        loaded = self.manager.load_checkpoint("test_cp_001")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.checkpoint_id, checkpoint.checkpoint_id)
        self.assertEqual(loaded.task_id, checkpoint.task_id)
        self.assertEqual(loaded.step_name, checkpoint.step_name)
        self.assertEqual(loaded.progress_percentage, 33.3)
    
    def test_checkpoint_hash_integrity(self):
        """测试检查点数据完整性校验"""
        checkpoint = Checkpoint(
            checkpoint_id="test_cp_002",
            task_id="task_001",
            step_id="step_1",
            step_name="测试步骤",
            agent_id="test_agent",
            status=CheckpointStatus.ACTIVE
        )
        
        self.manager.save_checkpoint(checkpoint)
        loaded = self.manager.load_checkpoint("test_cp_002")
        
        # 验证哈希
        self.assertEqual(loaded.checkpoint_hash, checkpoint.checkpoint_hash)
    
    def test_latest_checkpoint(self):
        """测试获取最新检查点"""
        # 创建多个检查点
        for i in range(3):
            checkpoint = Checkpoint(
                checkpoint_id=f"test_cp_latest_{i}",
                task_id="task_latest",
                step_id=f"step_{i}",
                step_name=f"步骤 {i}",
                agent_id="test_agent",
                status=CheckpointStatus.ACTIVE
            )
            self.manager.save_checkpoint(checkpoint)
        
        # 获取最新
        latest = self.manager.get_latest_checkpoint("task_latest")
        self.assertIsNotNone(latest)
        self.assertEqual(latest.checkpoint_id, "test_cp_latest_2")
    
    def test_delete_checkpoint(self):
        """测试删除检查点"""
        checkpoint = Checkpoint(
            checkpoint_id="test_cp_delete",
            task_id="task_001",
            step_id="step_1",
            step_name="测试步骤",
            agent_id="test_agent",
            status=CheckpointStatus.ACTIVE
        )
        
        self.manager.save_checkpoint(checkpoint)
        self.assertTrue(self.manager.delete_checkpoint("test_cp_delete"))
        
        # 验证删除
        loaded = self.manager.load_checkpoint("test_cp_delete")
        self.assertIsNone(loaded)
    
    def test_create_checkpoint_from_workflow(self):
        """测试从工作流状态创建检查点"""
        workflow_state = {
            'completed_steps': ['step_1', 'step_2'],
            'remaining_steps': ['step_3', 'step_4'],
            'context_snapshot': {'ctx': 'data'},
            'variables': {'var': 'value'}
        }
        
        checkpoint = self.manager.create_checkpoint_from_workflow(
            task_id="workflow_001",
            step_id="step_3",
            step_name="当前步骤",
            agent_id="developer",
            workflow_state=workflow_state
        )
        
        self.assertIsNotNone(checkpoint)
        self.assertEqual(checkpoint.task_id, "workflow_001")
        self.assertEqual(len(checkpoint.completed_steps), 2)
        self.assertEqual(checkpoint.progress_percentage, 50.0)


class TestHandoffDocument(unittest.TestCase):
    """交接文档测试类"""
    
    def test_create_handoff_document(self):
        """测试创建交接文档"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(tmpdir)
            
            handoff = manager.create_handoff_document(
                task_id="task_handoff_001",
                from_agent="architect",
                to_agent="developer",
                completed_work=["架构设计完成", "技术选型完成"],
                current_state={"架构文档": "已完成"},
                next_steps=["用户模块开发", "订单模块开发"],
                pending_issues=["需要确定数据库选型"],
                important_notes=["注意兼容性"],
                context_for_next={"架构文档路径": "/docs/arch.md"}
            )
            
            self.assertIsNotNone(handoff)
            self.assertEqual(handoff.from_agent, "architect")
            self.assertEqual(handoff.to_agent, "developer")
            self.assertEqual(len(handoff.completed_work), 2)
    
    def test_handoff_markdown_conversion(self):
        """测试交接文档 Markdown 格式转换"""
        handoff = HandoffDocument(
            handoff_id="hf_001",
            task_id="task_001",
            from_agent="architect",
            to_agent="developer",
            completed_work=["架构设计完成"],
            current_state={"status": "设计中"},
            next_steps=["开发阶段"],
            pending_issues=["问题1"],
            important_notes=["注意1"]
        )
        
        md = handoff.to_markdown()
        
        self.assertIn("交接文档", md)
        self.assertIn("architect", md)
        self.assertIn("developer", md)
        self.assertIn("架构设计完成", md)
    
    def test_save_and_load_handoff(self):
        """测试交接文档保存和加载"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CheckpointManager(tmpdir)
            
            handoff = manager.create_handoff_document(
                task_id="task_001",
                from_agent="pm",
                to_agent="dev",
                completed_work=["work1"],
                current_state={"s": "v"},
                next_steps=["next"]
            )
            
            # 加载
            loaded = manager.load_handoff(handoff.handoff_id)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.from_agent, "pm")
            self.assertEqual(loaded.to_agent, "dev")


if __name__ == '__main__':
    print("=" * 60)
    print("运行 CheckpointManager 单元测试")
    print("=" * 60)
    
    unittest.main(verbosity=2)