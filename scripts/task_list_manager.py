#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TaskListManager - 任务清单管理器

基于 Anthropic 文章《Effective Harnesses for Long-Running Agents》的核心思想：
- 像人类工程师一样维护任务清单（TODO.md）
- 支持任务拆解和优先级排序
- 跟踪任务进度和状态
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"  # 待处理
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    BLOCKED = "blocked"  # 被阻塞
    CANCELLED = "cancelled"  # 已取消


class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = 1  # 紧急重要
    HIGH = 2  # 高优先级
    MEDIUM = 3  # 中优先级
    LOW = 4  # 低优先级


@dataclass
class TaskItem:
    """
    任务项数据模型
    
    表示一个具体的任务，包含：
    - 基本信息（ID、标题、描述）
    - 状态和优先级
    - 负责角色
    - 依赖关系
    - 预估和实际工时
    """
    task_id: str
    title: str
    description: str = ""
    
    # 状态和优先级
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    
    # 负责角色
    assigned_agent: str = ""  # 负责的 Agent
    created_by: str = ""  # 创建者
    
    # 依赖关系
    depends_on: List[str] = field(default_factory=list)  # 依赖的任务 ID 列表
    blocked_by: List[str] = field(default_factory=list)  # 阻塞此任务的任务 ID 列表
    
    # 时间和工时
    estimated_hours: float = 0.0  # 预估工时
    actual_hours: float = 0.0  # 实际工时
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    due_date: Optional[str] = None
    
    # 标签和分类
    tags: List[str] = field(default_factory=list)
    category: str = ""  # 任务分类：需求、设计、开发、测试、发布等
    
    # 输出和产物
    outputs: List[str] = field(default_factory=list)  # 任务产生的文件/产物
    acceptance_criteria: List[str] = field(default_factory=list)  # 验收标准
    
    # 备注
    notes: str = ""
    comments: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value if isinstance(self.status, TaskStatus) else self.status,
            'priority': self.priority.value if isinstance(self.priority, TaskPriority) else self.priority,
            'assigned_agent': self.assigned_agent,
            'created_by': self.created_by,
            'depends_on': self.depends_on,
            'blocked_by': self.blocked_by,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'due_date': self.due_date,
            'tags': self.tags,
            'category': self.category,
            'outputs': self.outputs,
            'acceptance_criteria': self.acceptance_criteria,
            'notes': self.notes,
            'comments': self.comments
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskItem':
        """从字典创建"""
        # 创建副本避免修改原始数据
        data_copy = dict(data)
        # 转换枚举
        if isinstance(data_copy.get('status'), str):
            data_copy['status'] = TaskStatus(data_copy['status'])
        if isinstance(data_copy.get('priority'), int):
            data_copy['priority'] = TaskPriority(data_copy['priority'])
        return cls(**data_copy)
    
    def is_ready(self, all_tasks: Dict[str, 'TaskItem']) -> bool:
        """
        检查任务是否准备就绪（依赖是否都已完成）
        
        Args:
            all_tasks: 所有任务的字典
            
        Returns:
            bool: 是否准备就绪
        """
        if self.status != TaskStatus.PENDING:
            return False
        
        for dep_id in self.depends_on:
            dep_task = all_tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        
        return True


@dataclass
class TaskList:
    """
    任务清单数据模型
    
    表示一个完整的任务清单，包含多个任务项
    """
    tasklist_id: str
    name: str
    description: str = ""
    
    # 任务列表
    tasks: List[TaskItem] = field(default_factory=list)
    
    # 任务清单状态
    status: str = "active"  # active, completed, archived
    
    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = ""
    
    # 统计信息
    total_hours: float = 0.0
    completed_hours: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'tasklist_id': self.tasklist_id,
            'name': self.name,
            'description': self.description,
            'tasks': [t.to_dict() for t in self.tasks] if isinstance(self.tasks, list) else self.tasks,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by,
            'total_hours': self.total_hours,
            'completed_hours': self.completed_hours
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskList':
        """从字典创建"""
        # 转换任务列表
        if 'tasks' in data:
            data['tasks'] = [TaskItem.from_dict(t) for t in data['tasks']]
        return cls(**data)
    
    def get_progress(self) -> float:
        """
        计算任务清单的完成进度
        
        Returns:
            float: 完成百分比 (0-100)
        """
        if not self.tasks:
            return 0.0
        
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        return (completed / len(self.tasks)) * 100
    
    def get_ready_tasks(self) -> List[TaskItem]:
        """
        获取准备就绪的任务（依赖都已完成）
        
        Returns:
            List[TaskItem]: 准备就绪的任务列表
        """
        all_tasks = {t.task_id: t for t in self.tasks}
        return [t for t in self.tasks if t.is_ready(all_tasks)]


class TaskListManager:
    """
    任务清单管理器
    
    核心功能：
    1. 任务清单的创建、读取、更新、删除
    2. 任务项的添加、修改、删除
    3. 依赖关系管理
    4. 优先级排序
    5. 进度跟踪
    6. 导出为 Markdown 格式（像 TODO.md）
    
    使用场景：
    - 工作流引擎的任务拆分
    - 多 Agent 协作时的任务分配
    - 人类工程师的任务管理
    """
    
    def __init__(self, storage_path: str = "./tasklists"):
        """
        初始化任务清单管理器
        
        Args:
            storage_path: 任务清单存储路径
        """
        self.storage_path = Path(storage_path)
        self.tasklists_dir = self.storage_path / "lists"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.tasklists_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_tasklist_path(self, tasklist_id: str) -> Path:
        """获取任务清单文件路径"""
        return self.tasklists_dir / f"{tasklist_id}.json"
    
    def create_tasklist(
        self,
        name: str,
        description: str = "",
        created_by: str = ""
    ) -> TaskList:
        """
        创建新的任务清单
        
        Args:
            name: 任务清单名称
            description: 任务清单描述
            created_by: 创建者
            
        Returns:
            TaskList: 创建的任务清单
        """
        tasklist = TaskList(
            tasklist_id=f"tl_{uuid.uuid4().hex[:12]}",
            name=name,
            description=description,
            created_by=created_by
        )
        
        self.save_tasklist(tasklist)
        return tasklist
    
    def save_tasklist(self, tasklist: TaskList) -> bool:
        """
        保存任务清单
        
        Args:
            tasklist: 任务清单
            
        Returns:
            bool: 是否保存成功
        """
        try:
            tasklist.updated_at = datetime.now().isoformat()
            path = self._get_tasklist_path(tasklist.tasklist_id)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(tasklist.to_dict(), f, indent=2, ensure_ascii=False)
            
            print(f"💾 任务清单已保存: {tasklist.name} ({len(tasklist.tasks)} 个任务)")
            return True
            
        except Exception as e:
            print(f"❌ 保存任务清单失败: {e}")
            return False
    
    def load_tasklist(self, tasklist_id: str) -> Optional[TaskList]:
        """
        加载任务清单
        
        Args:
            tasklist_id: 任务清单 ID
            
        Returns:
            Optional[TaskList]: 任务清单
        """
        try:
            path = self._get_tasklist_path(tasklist_id)
            if not path.exists():
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return TaskList.from_dict(data)
            
        except Exception as e:
            print(f"❌ 加载任务清单失败: {e}")
            return None
    
    def delete_tasklist(self, tasklist_id: str) -> bool:
        """
        删除任务清单
        
        Args:
            tasklist_id: 任务清单 ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            path = self._get_tasklist_path(tasklist_id)
            if path.exists():
                path.unlink()
                print(f"🗑️ 任务清单已删除: {tasklist_id}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ 删除任务清单失败: {e}")
            return False
    
    def add_task(
        self,
        tasklist_id: str,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        assigned_agent: str = "",
        depends_on: List[str] = None,
        estimated_hours: float = 0.0,
        tags: List[str] = None,
        category: str = ""
    ) -> Optional[TaskItem]:
        """
        向任务清单添加任务
        
        Args:
            tasklist_id: 任务清单 ID
            title: 任务标题
            description: 任务描述
            priority: 优先级
            assigned_agent: 负责的 Agent
            depends_on: 依赖的任务 ID 列表
            estimated_hours: 预估工时
            tags: 标签列表
            category: 任务分类
            
        Returns:
            Optional[TaskItem]: 创建的任务项
        """
        tasklist = self.load_tasklist(tasklist_id)
        if not tasklist:
            return None
        
        task = TaskItem(
            task_id=f"task_{uuid.uuid4().hex[:12]}",
            title=title,
            description=description,
            priority=priority,
            assigned_agent=assigned_agent,
            depends_on=depends_on or [],
            estimated_hours=estimated_hours,
            tags=tags or [],
            category=category
        )
        
        tasklist.tasks.append(task)
        tasklist.total_hours += estimated_hours
        self.save_tasklist(tasklist)
        
        return task
    
    def update_task_status(
        self,
        tasklist_id: str,
        task_id: str,
        status: TaskStatus
    ) -> bool:
        """
        更新任务状态
        
        Args:
            tasklist_id: 任务清单 ID
            task_id: 任务 ID
            status: 新状态
            
        Returns:
            bool: 是否更新成功
        """
        tasklist = self.load_tasklist(tasklist_id)
        if not tasklist:
            return False
        
        for task in tasklist.tasks:
            if task.task_id == task_id:
                old_status = task.status
                task.status = status
                
                # 更新相关时间
                now = datetime.now().isoformat()
                if status == TaskStatus.IN_PROGRESS and not task.started_at:
                    task.started_at = now
                elif status == TaskStatus.COMPLETED:
                    task.completed_at = now
                    tasklist.completed_hours += task.estimated_hours
                
                self.save_tasklist(tasklist)
                print(f"📝 任务状态更新: {task.title} ({old_status.value} → {status.value})")
                return True
        
        return False
    
    def get_next_task(
        self,
        tasklist_id: str,
        agent_id: str = None
    ) -> Optional[TaskItem]:
        """
        获取下一个可执行的任务
        
        优先级规则：
        1. 准备就绪（依赖都完成）
        2. 按优先级排序（CRITICAL > HIGH > MEDIUM > LOW）
        3. 如果指定了 agent_id，优先返回该 Agent 的任务
        
        Args:
            tasklist_id: 任务清单 ID
            agent_id: 可选的 Agent ID 过滤
            
        Returns:
            Optional[TaskItem]: 下一个任务
        """
        tasklist = self.load_tasklist(tasklist_id)
        if not tasklist:
            return None
        
        # 获取准备就绪的任务
        ready_tasks = tasklist.get_ready_tasks()
        
        if not ready_tasks:
            return None
        
        # 按优先级排序
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        ready_tasks.sort(key=lambda t: priority_order.get(t.priority, 99))
        
        # 如果指定了 agent_id，优先返回匹配的任务
        if agent_id:
            agent_tasks = [t for t in ready_tasks if t.assigned_agent == agent_id]
            if agent_tasks:
                return agent_tasks[0]
        
        return ready_tasks[0]
    
    def export_to_markdown(self, tasklist_id: str, output_path: str = None) -> str:
        """
        导出任务清单为 Markdown 格式（像 TODO.md）
        
        Args:
            tasklist_id: 任务清单 ID
            output_path: 可选的输出文件路径
            
        Returns:
            str: Markdown 格式的内容
        """
        tasklist = self.load_tasklist(tasklist_id)
        if not tasklist:
            return ""
        
        md = f"# {tasklist.name}\n\n"
        md += f"{tasklist.description}\n\n"
        
        # 进度统计
        progress = tasklist.get_progress()
        completed = sum(1 for t in tasklist.tasks if t.status == TaskStatus.COMPLETED)
        total = len(tasklist.tasks)
        
        md += f"**进度**: {completed}/{total} ({progress:.1%})\n\n"
        md += f"- 创建时间: {tasklist.created_at}\n"
        md += f"- 更新时间: {tasklist.updated_at}\n\n"
        
        # 按状态分组
        pending_tasks = [t for t in tasklist.tasks if t.status == TaskStatus.PENDING]
        in_progress_tasks = [t for t in tasklist.tasks if t.status == TaskStatus.IN_PROGRESS]
        completed_tasks = [t for t in tasklist.tasks if t.status == TaskStatus.COMPLETED]
        
        # 进行中的任务
        if in_progress_tasks:
            md += "## 🚧 进行中\n\n"
            for task in in_progress_tasks:
                md += self._task_to_markdown(task)
                md += "\n"
        
        # 待处理的任务
        if pending_tasks:
            md += "## 📋 待处理\n\n"
            for task in sorted(pending_tasks, key=lambda t: t.priority.value):
                md += self._task_to_markdown(task)
                md += "\n"
        
        # 已完成的任务
        if completed_tasks:
            md += "## ✅ 已完成\n\n"
            for task in completed_tasks:
                md += self._task_to_markdown(task)
                md += "\n"
        
        # 保存到文件
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md)
            print(f"📄 任务清单已导出: {output_path}")
        
        return md
    
    def _task_to_markdown(self, task: TaskItem) -> str:
        """
        将任务项转换为 Markdown 格式
        
        Args:
            task: 任务项
            
        Returns:
            str: Markdown 格式
        """
        # 状态图标
        status_icons = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.BLOCKED: "🚫",
            TaskStatus.CANCELLED: "❌"
        }
        
        # 优先级图标
        priority_icons = {
            TaskPriority.CRITICAL: "🔴",
            TaskPriority.HIGH: "🟠",
            TaskPriority.MEDIUM: "🟡",
            TaskPriority.LOW: "🟢"
        }
        
        md = f"### {status_icons.get(task.status, '📌')} {task.title}\n\n"
        md += f"- **ID**: `{task.task_id}`\n"
        md += f"- **优先级**: {priority_icons.get(task.priority, '⚪')} "
        md += f"{task.priority.name if isinstance(task.priority, TaskPriority) else task.priority}\n"
        
        if task.assigned_agent:
            md += f"- **负责人**: {task.assigned_agent}\n"
        
        if task.estimated_hours > 0:
            md += f"- **预估工时**: {task.estimated_hours}h\n"
        
        if task.depends_on:
            md += f"- **依赖**: {', '.join([f'`{d}`' for d in task.depends_on])}\n"
        
        if task.tags:
            md += f"- **标签**: {' '.join([f'`{tag}`' for tag in task.tags])}\n"
        
        if task.category:
            md += f"- **分类**: {task.category}\n"
        
        if task.description:
            md += f"\n{task.description}\n"
        
        if task.acceptance_criteria:
            md += "\n**验收标准:**\n"
            for criteria in task.acceptance_criteria:
                md += f"- [ ] {criteria}\n"
        
        return md
    
    def list_tasklists(self) -> List[Dict[str, Any]]:
        """
        列出所有任务清单
        
        Returns:
            List[Dict[str, Any]]: 任务清单摘要列表
        """
        try:
            tasklists = []
            for path in self.tasklists_dir.glob("*.json"):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 只返回摘要信息
                    summary = {
                        'tasklist_id': data.get('tasklist_id'),
                        'name': data.get('name'),
                        'description': data.get('description'),
                        'task_count': len(data.get('tasks', [])),
                        'progress': data.get('completed_hours', 0) / data.get('total_hours', 1) * 100 if data.get('total_hours', 0) > 0 else 0,
                        'updated_at': data.get('updated_at')
                    }
                    tasklists.append(summary)
            
            # 按更新时间排序
            tasklists.sort(key=lambda x: x['updated_at'] or '', reverse=True)
            return tasklists
            
        except Exception as e:
            print(f"❌ 列出任务清单失败: {e}")
            return []


if __name__ == "__main__":
    # 演示 TaskListManager 的使用
    print("=" * 60)
    print("TaskListManager 演示")
    print("=" * 60)
    
    # 创建任务清单管理器
    manager = TaskListManager("./test_tasklists")
    
    # 创建任务清单
    tasklist = manager.create_tasklist(
        name="电商系统开发",
        description="电商系统全生命周期开发任务清单",
        created_by="product-manager"
    )
    
    # 添加任务
    task1 = manager.add_task(
        tasklist_id=tasklist.tasklist_id,
        title="需求分析",
        description="完成电商系统的需求调研和分析",
        priority=TaskPriority.HIGH,
        assigned_agent="product-manager",
        estimated_hours=8.0,
        category="需求"
    )
    
    task2 = manager.add_task(
        tasklist_id=tasklist.tasklist_id,
        title="架构设计",
        description="设计电商系统的技术架构",
        priority=TaskPriority.HIGH,
        assigned_agent="architect",
        estimated_hours=16.0,
        depends_on=[task1.task_id] if task1 else [],
        category="设计"
    )
    
    task3 = manager.add_task(
        tasklist_id=tasklist.tasklist_id,
        title="用户模块开发",
        description="实现用户注册、登录、权限管理",
        priority=TaskPriority.MEDIUM,
        assigned_agent="solo-coder",
        estimated_hours=40.0,
        depends_on=[task2.task_id] if task2 else [],
        category="开发"
    )
    
    # 导出为 Markdown
    print("\n📄 生成 Markdown 任务清单:")
    print("-" * 60)
    md = manager.export_to_markdown(tasklist.tasklist_id)
    print(md)
    
    # 获取下一个任务
    next_task = manager.get_next_task(tasklist.tasklist_id)
    if next_task:
        print(f"\n🎯 下一个任务: {next_task.title} (分配给: {next_task.assigned_agent})")
    
    # 清理测试数据
    import shutil
    shutil.rmtree("./test_tasklists", ignore_errors=True)
    
    print("\n✅ 演示完成")