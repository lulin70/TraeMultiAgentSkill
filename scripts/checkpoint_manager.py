#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CheckpointManager - 任务状态检查点管理器

基于 Anthropic 文章《Effective Harnesses for Long-Running Agents》的核心思想：
- 像人类工程师一样定期保存进度
- 支持从断点恢复，避免"断片"问题
- 为长时间运行的任务提供可靠性保障
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import shutil
import hashlib


class CheckpointStatus(Enum):
    """检查点状态"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class Checkpoint:
    """
    检查点数据模型
    
    记录任务在某个时间点的完整状态，包括：
    - 当前执行位置
    - 已完成的步骤
    - 上下文数据
    - 变量状态
    """
    checkpoint_id: str
    task_id: str
    step_id: str  # 当前步骤 ID
    step_name: str  # 当前步骤名称
    agent_id: str  # 当前负责的 Agent
    status: CheckpointStatus
    
    # 进度信息
    completed_steps: List[str] = field(default_factory=list)
    remaining_steps: List[str] = field(default_factory=list)
    progress_percentage: float = 0.0
    
    # 上下文和状态
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    
    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None  # 过期时间
    checkpoint_hash: str = ""  # 数据完整性校验
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = {
            'checkpoint_id': self.checkpoint_id,
            'task_id': self.task_id,
            'step_id': self.step_id,
            'step_name': self.step_name,
            'agent_id': self.agent_id,
            'status': self.status.value if isinstance(self.status, CheckpointStatus) else self.status,
            'completed_steps': self.completed_steps,
            'remaining_steps': self.remaining_steps,
            'progress_percentage': self.progress_percentage,
            'context_snapshot': self.context_snapshot,
            'variables': self.variables,
            'outputs': self.outputs,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'expires_at': self.expires_at,
            'checkpoint_hash': self.checkpoint_hash
        }
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checkpoint':
        """从字典创建"""
        # 创建副本避免修改原始数据
        data_copy = dict(data)
        # 转换状态枚举
        if isinstance(data_copy.get('status'), str):
            data_copy['status'] = CheckpointStatus(data_copy['status'])
        return cls(**data_copy)


@dataclass
class HandoffDocument:
    """
    交接文档
    
    当一个 Agent 需要交接任务给另一个 Agent 时，生成标准化的交接文档
    """
    handoff_id: str
    task_id: str
    from_agent: str  # 交出任务的 Agent
    to_agent: str  # 接收任务的 Agent
    
    # 交接内容
    completed_work: List[str] = field(default_factory=list)  # 已完成的工作
    current_state: Dict[str, Any] = field(default_factory=dict)  # 当前状态
    next_steps: List[str] = field(default_factory=list)  # 下一步骤
    pending_issues: List[str] = field(default_factory=list)  # 待处理问题
    important_notes: List[str] = field(default_factory=list)  # 重要注意事项
    
    # 上下文传递
    context_for_next: Dict[str, Any] = field(default_factory=dict)  # 传递给下一个 Agent 的上下文
    accumulated_knowledge: Dict[str, Any] = field(default_factory=dict)  # 积累的知识
    
    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    handoff_reason: str = "task_completed"  # 交接原因
    confidence: float = 1.0  # 交接信心度
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HandoffDocument':
        """从字典创建"""
        return cls(**data)
    
    def to_markdown(self) -> str:
        """
        转换为 Markdown 格式，方便阅读
        
        Returns:
            str: Markdown 格式的交接文档
        """
        md = f"""# 任务交接文档

## 基本信息
- **交接 ID**: {self.handoff_id}
- **任务 ID**: {self.task_id}
- **交接时间**: {self.created_at}
- **交接原因**: {self.handoff_reason}
- **信心度**: {self.confidence:.0%}

## 交接方 → 接收方
- **从**: {self.from_agent}
- **到**: {self.to_agent}

---

## ✅ 已完成的工作
"""
        for i, work in enumerate(self.completed_work, 1):
            md += f"{i}. {work}\n"
        
        md += f"\n## 📊 当前状态\n\n```json\n{json.dumps(self.current_state, indent=2, ensure_ascii=False)}\n```\n"
        
        md += f"\n## 🎯 下一步骤\n"
        for i, step in enumerate(self.next_steps, 1):
            md += f"{i}. {step}\n"
        
        if self.pending_issues:
            md += f"\n## ⚠️ 待处理问题\n"
            for i, issue in enumerate(self.pending_issues, 1):
                md += f"{i}. {issue}\n"
        
        if self.important_notes:
            md += f"\n## 📝 重要注意事项\n"
            for i, note in enumerate(self.important_notes, 1):
                md += f"- {note}\n"
        
        md += f"\n## 🔄 传递给下一个 Agent 的上下文\n\n```json\n{json.dumps(self.context_for_next, indent=2, ensure_ascii=False)}\n```\n"
        
        return md


class CheckpointManager:
    """
    检查点管理器
    
    核心功能：
    1. 定期保存任务状态（像人类工程师定期 git commit）
    2. 支持从任意检查点恢复
    3. 自动生成交接文档
    4. 数据完整性校验
    5. 过期检查点自动清理
    
    使用场景：
    - 长时间运行的任务
    - 可能中断的任务
    - 需要多个 Agent 协作的任务
    - 需要断点恢复的场景
    """
    
    def __init__(self, storage_path: str = "./checkpoints"):
        """
        初始化检查点管理器
        
        Args:
            storage_path: 检查点存储路径
        """
        self.storage_path = Path(storage_path)
        self.checkpoints_dir = self.storage_path / "checkpoints"
        self.handoffs_dir = self.storage_path / "handoffs"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.handoffs_dir.mkdir(parents=True, exist_ok=True)
    
    def _compute_hash(self, data: Dict[str, Any]) -> str:
        """
        计算数据的哈希值，用于完整性校验
        
        Args:
            data: 要计算哈希的数据
            
        Returns:
            str: SHA256 哈希值
        """
        # 排除 checkpoint_hash 字段，避免循环依赖
        data_for_hash = {k: v for k, v in data.items() if k != 'checkpoint_hash'}
        json_str = json.dumps(data_for_hash, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def _get_checkpoint_path(self, checkpoint_id: str) -> Path:
        """获取检查点文件路径"""
        return self.checkpoints_dir / f"{checkpoint_id}.json"
    
    def _get_handoff_path(self, handoff_id: str) -> Path:
        """获取交接文档文件路径"""
        return self.handoffs_dir / f"{handoff_id}.json"
    
    def save_checkpoint(self, checkpoint: Checkpoint) -> bool:
        """
        保存检查点
        
        定期调用此方法保存任务状态，类似于人类工程师的 git commit
        
        Args:
            checkpoint: 检查点数据
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 1. 首先更新 checkpoint_hash（这会设置 checkpoint 对象的 checkpoint_hash）
            checkpoint.updated_at = datetime.now().isoformat()
            checkpoint_dict_for_hash = checkpoint.to_dict()
            checkpoint.checkpoint_hash = self._compute_hash(checkpoint_dict_for_hash)
            
            # 2. 获取最终的字典（包含已设置的 checkpoint_hash）
            checkpoint_dict = checkpoint.to_dict()
            
            # 3. 确保字典中的 checkpoint_hash 与对象一致
            checkpoint_dict['checkpoint_hash'] = checkpoint.checkpoint_hash
            
            # 4. 保存到文件
            checkpoint_path = self._get_checkpoint_path(checkpoint.checkpoint_id)
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_dict, f, indent=2, ensure_ascii=False)
            
            print(f"💾 检查点已保存: {checkpoint.checkpoint_id} (进度: {checkpoint.progress_percentage:.1%})")
            return True
            
        except Exception as e:
            print(f"❌ 保存检查点失败: {e}")
            return False
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        加载检查点
        
        Args:
            checkpoint_id: 检查点 ID
            
        Returns:
            Optional[Checkpoint]: 检查点数据，如果不存在则返回 None
        """
        try:
            checkpoint_path = self._get_checkpoint_path(checkpoint_id)
            if not checkpoint_path.exists():
                print(f"⚠️  检查点不存在: {checkpoint_id}")
                return None
            
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            checkpoint = Checkpoint.from_dict(data)
            
            # 验证数据完整性
            computed_hash = self._compute_hash({k: v for k, v in data.items() if k != 'checkpoint_hash'})
            if computed_hash != checkpoint.checkpoint_hash:
                print(f"⚠️  检查点数据完整性校验失败: {checkpoint_id}")
                return None
            
            print(f"📂 检查点已加载: {checkpoint_id}")
            return checkpoint
            
        except Exception as e:
            print(f"❌ 加载检查点失败: {e}")
            return None
    
    def get_latest_checkpoint(self, task_id: str) -> Optional[Checkpoint]:
        """
        获取某个任务的最新检查点
        
        Args:
            task_id: 任务 ID
            
        Returns:
            Optional[Checkpoint]: 最新检查点
        """
        try:
            checkpoints = list(self.checkpoints_dir.glob(f"*.json"))
            task_checkpoints = []
            
            for cp_path in checkpoints:
                with open(cp_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('task_id') == task_id:
                        task_checkpoints.append((cp_path.stat().st_mtime, Checkpoint.from_dict(data)))
            
            if not task_checkpoints:
                return None
            
            # 返回最新的检查点
            latest = sorted(task_checkpoints, key=lambda x: x[0], reverse=True)[0][1]
            return latest
            
        except Exception as e:
            print(f"❌ 获取最新检查点失败: {e}")
            return None
    
    def list_checkpoints(self, task_id: Optional[str] = None) -> List[Checkpoint]:
        """
        列出所有检查点
        
        Args:
            task_id: 可选的任务 ID 过滤
            
        Returns:
            List[Checkpoint]: 检查点列表
        """
        try:
            checkpoints = []
            for cp_path in self.checkpoints_dir.glob("*.json"):
                with open(cp_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if task_id is None or data.get('task_id') == task_id:
                        checkpoints.append(Checkpoint.from_dict(data))
            
            # 按时间排序，最新的在前
            checkpoints.sort(key=lambda x: x.created_at, reverse=True)
            return checkpoints
            
        except Exception as e:
            print(f"❌ 列出检查点失败: {e}")
            return []
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """
        删除检查点
        
        Args:
            checkpoint_id: 检查点 ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            checkpoint_path = self._get_checkpoint_path(checkpoint_id)
            if checkpoint_path.exists():
                checkpoint_path.unlink()
                print(f"🗑️  检查点已删除: {checkpoint_id}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ 删除检查点失败: {e}")
            return False
    
    def cleanup_expired_checkpoints(self, max_age_hours: int = 24) -> int:
        """
        清理过期的检查点
        
        Args:
            max_age_hours: 最大保留时间（小时）
            
        Returns:
            int: 清理的检查点数量
        """
        try:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            cleaned_count = 0
            
            for cp_path in self.checkpoints_dir.glob("*.json"):
                if cp_path.stat().st_mtime < cutoff_time.timestamp():
                    cp_path.unlink()
                    cleaned_count += 1
            
            if cleaned_count > 0:
                print(f"🧹 已清理 {cleaned_count} 个过期检查点")
            
            return cleaned_count
            
        except Exception as e:
            print(f"❌ 清理过期检查点失败: {e}")
            return 0
    
    def save_handoff(self, handoff: HandoffDocument) -> bool:
        """
        保存交接文档
        
        Args:
            handoff: 交接文档
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 保存 JSON 版本
            handoff_path = self._get_handoff_path(handoff.handoff_id)
            with open(handoff_path, 'w', encoding='utf-8') as f:
                json.dump(handoff.to_dict(), f, indent=2, ensure_ascii=False)
            
            # 同时保存 Markdown 版本
            md_path = handoff_path.with_suffix('.md')
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(handoff.to_markdown())
            
            print(f"📄 交接文档已保存: {handoff.handoff_id}")
            print(f"   从 {handoff.from_agent} → 到 {handoff.to_agent}")
            return True
            
        except Exception as e:
            print(f"❌ 保存交接文档失败: {e}")
            return False
    
    def load_handoff(self, handoff_id: str) -> Optional[HandoffDocument]:
        """
        加载交接文档
        
        Args:
            handoff_id: 交接文档 ID
            
        Returns:
            Optional[HandoffDocument]: 交接文档
        """
        try:
            handoff_path = self._get_handoff_path(handoff_id)
            if not handoff_path.exists():
                return None
            
            with open(handoff_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return HandoffDocument.from_dict(data)
            
        except Exception as e:
            print(f"❌ 加载交接文档失败: {e}")
            return None
    
    def get_task_handoffs(self, task_id: str) -> List[HandoffDocument]:
        """
        获取某个任务的所有交接文档
        
        Args:
            task_id: 任务 ID
            
        Returns:
            List[HandoffDocument]: 交接文档列表
        """
        try:
            handoffs = []
            for hf_path in self.handoffs_dir.glob("*.json"):
                with open(hf_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('task_id') == task_id:
                        handoffs.append(HandoffDocument.from_dict(data))
            
            # 按时间排序
            handoffs.sort(key=lambda x: x.created_at)
            return handoffs
            
        except Exception as e:
            print(f"❌ 获取交接文档失败: {e}")
            return []
    
    def create_checkpoint_from_workflow(
        self,
        task_id: str,
        step_id: str,
        step_name: str,
        agent_id: str,
        workflow_state: Dict[str, Any]
    ) -> Checkpoint:
        """
        从工作流状态创建检查点
        
        这是一个便捷方法，用于在工作流执行过程中快速创建检查点
        
        Args:
            task_id: 任务 ID
            step_id: 当前步骤 ID
            step_name: 当前步骤名称
            agent_id: 当前 Agent ID
            workflow_state: 工作流状态（包含 completed_steps, remaining_steps 等）
            
        Returns:
            Checkpoint: 创建的检查点
        """
        completed = workflow_state.get('completed_steps', [])
        remaining = workflow_state.get('remaining_steps', [])
        total = len(completed) + len(remaining)
        progress = len(completed) / total if total > 0 else 0.0
        
        checkpoint = Checkpoint(
            checkpoint_id=f"cp_{task_id}_{step_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task_id=task_id,
            step_id=step_id,
            step_name=step_name,
            agent_id=agent_id,
            status=CheckpointStatus.ACTIVE,
            completed_steps=completed,
            remaining_steps=remaining,
            progress_percentage=progress * 100,
            context_snapshot=workflow_state.get('context_snapshot', {}),
            variables=workflow_state.get('variables', {}),
            outputs=workflow_state.get('outputs', {})
        )
        
        self.save_checkpoint(checkpoint)
        return checkpoint
    
    def create_handoff_document(
        self,
        task_id: str,
        from_agent: str,
        to_agent: str,
        completed_work: List[str],
        current_state: Dict[str, Any],
        next_steps: List[str],
        pending_issues: List[str] = None,
        important_notes: List[str] = None,
        context_for_next: Dict[str, Any] = None
    ) -> HandoffDocument:
        """
        创建交接文档
        
        这是一个便捷方法，用于在 Agent 交接时生成标准化的交接文档
        
        Args:
            task_id: 任务 ID
            from_agent: 交出任务的 Agent
            to_agent: 接收任务的 Agent
            completed_work: 已完成的工作列表
            current_state: 当前状态
            next_steps: 下一步骤列表
            pending_issues: 待处理问题列表
            important_notes: 重要注意事项列表
            context_for_next: 传递给下一个 Agent 的上下文
            
        Returns:
            HandoffDocument: 创建的交接文档
        """
        handoff = HandoffDocument(
            handoff_id=f"hf_{task_id}_{from_agent}_{to_agent}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task_id=task_id,
            from_agent=from_agent,
            to_agent=to_agent,
            completed_work=completed_work,
            current_state=current_state,
            next_steps=next_steps,
            pending_issues=pending_issues or [],
            important_notes=important_notes or [],
            context_for_next=context_for_next or {},
            handoff_reason="task_completed"
        )
        
        self.save_handoff(handoff)
        return handoff


if __name__ == "__main__":
    # 演示 CheckpointManager 的使用
    print("=" * 60)
    print("CheckpointManager 演示")
    print("=" * 60)
    
    # 创建检查点管理器
    manager = CheckpointManager("./test_checkpoints")
    
    # 创建检查点
    checkpoint = Checkpoint(
        checkpoint_id="cp_demo_001",
        task_id="task_demo",
        step_id="step_2",
        step_name="架构设计",
        agent_id="architect",
        status=CheckpointStatus.ACTIVE,
        completed_steps=["step_1_需求分析"],
        remaining_steps=["step_3_开发", "step_4_测试"],
        progress_percentage=33.3,
        context_snapshot={"需求文档": "已完成 v1.0"},
        variables={"技术栈": "Spring Cloud"}
    )
    
    manager.save_checkpoint(checkpoint)
    
    # 加载检查点
    loaded = manager.load_checkpoint("cp_demo_001")
    if loaded:
        print(f"\n✅ 加载成功: {loaded.step_name} (进度: {loaded.progress_percentage:.1%})")
    
    # 创建交接文档
    handoff = manager.create_handoff_document(
        task_id="task_demo",
        from_agent="architect",
        to_agent="developer",
        completed_work=["需求分析完成", "架构设计完成"],
        current_state={"架构文档": "已完成", "技术选型": "Spring Cloud + Docker"},
        next_steps=["用户模块开发", "订单模块开发"],
        pending_issues=["需要确定数据库选型"],
        important_notes=["注意兼容性", "保持接口向后兼容"],
        context_for_next={"架构文档路径": "/docs/architecture.md"}
    )
    
    print(f"\n📄 交接文档已生成")
    print(f"   Markdown 版本: {handoff.handoff_id}.md")
    
    # 清理测试数据
    import shutil
    shutil.rmtree("./test_checkpoints", ignore_errors=True)
    
    print("\n✅ 演示完成")