#!/usr/bin/env python3
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from .checkpoint_manager import CheckpointManager, Checkpoint, CheckpointStatus, HandoffDocument

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    WAITING_HANDOVER = "waiting_handover"


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    step_id: str = field(default_factory=lambda: f"step-{uuid.uuid4().hex[:6]}")
    name: str = ""
    description: str = ""
    role_id: str = ""
    action: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 3600
    retry_count: int = 3
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = {
            'step_id': self.step_id, 'name': self.name, 'description': self.description,
            'role_id': self.role_id, 'action': self.action, 'inputs': self.inputs,
            'outputs': self.outputs, 'conditions': self.conditions, 'timeout': self.timeout,
            'retry_count': self.retry_count,
            'status': self.status.value if isinstance(self.status, StepStatus) else self.status,
            'result': self.result, 'error': self.error,
        }
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowStep':
        data_copy = dict(data)
        if isinstance(data_copy.get('status'), str):
            try:
                data_copy['status'] = StepStatus(data_copy['status'])
            except ValueError:
                data_copy['status'] = StepStatus.PENDING
        return cls(**data_copy)


@dataclass
class WorkflowDefinition:
    workflow_id: str = field(default_factory=lambda: f"wf-{uuid.uuid4().hex[:8]}")
    name: str = ""
    description: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            'workflow_id': self.workflow_id, 'name': self.name, 'description': self.description,
            'steps': [s.to_dict() for s in self.steps], 'variables': self.variables,
            'metadata': self.metadata, 'created_at': self.created_at,
        }


@dataclass
class WorkflowInstance:
    instance_id: str = field(default_factory=lambda: f"inst-{uuid.uuid4().hex[:8]}")
    workflow_id: str = ""
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: Optional[str] = None
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: str = ""
    checkpoint_id: Optional[str] = None
    current_agent_id: Optional[str] = None
    handoff_history: List[str] = field(default_factory=list)


class WorkflowEngine:
    """
    Simplified workflow engine for DevSquad.

    Integrates with:
    - CheckpointManager for state persistence
    - Coordinator for task execution
    - Dispatcher for role-based dispatching

    Features:
    1. Task-to-workflow auto-splitting
    2. Step-by-step execution with checkpointing
    3. Agent handoff support
    4. Resume from checkpoint
    """

    def __init__(self, storage_path: str = "./workflows", coordinator=None, dispatcher=None):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.definitions: Dict[str, WorkflowDefinition] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self.executors: Dict[str, Callable] = {}

        self.coordinator = coordinator
        self.dispatcher = dispatcher
        self.checkpoint_manager = CheckpointManager(
            storage_path=str(self.storage_path / "checkpoints")
        )
        self.checkpoint_interval = 2

    def create_workflow_from_task(
        self,
        task_title: str,
        task_description: str = "",
        target_agent: str = None,
    ) -> WorkflowDefinition:
        """
        Create a workflow from a task description.

        Automatically splits the task into steps based on keyword analysis.
        """
        steps = self._split_task_into_steps(task_title, task_description)

        definition = WorkflowDefinition(
            name=task_title,
            description=task_description,
            steps=steps,
            metadata={
                'target_agent': target_agent,
                'created_by': 'WorkflowEngine',
            },
        )

        self.definitions[definition.workflow_id] = definition
        logger.info("Workflow created: %s (%d steps)", definition.workflow_id, len(steps))
        return definition

    def _split_task_into_steps(self, task_title: str, task_description: str) -> List[WorkflowStep]:
        steps = []
        task_text = f"{task_title} {task_description}".lower()

        is_architecture = any(kw in task_text for kw in ['architecture', 'design', 'system', '架构', '设计'])
        is_ui_design = any(kw in task_text for kw in ['ui', 'interface', 'frontend', '界面', '交互'])
        is_development = any(kw in task_text for kw in ['develop', 'implement', 'code', '开发', '实现', '编码'])
        is_testing = any(kw in task_text for kw in ['test', 'verify', 'quality', '测试', '验证'])
        is_product = any(kw in task_text for kw in ['requirement', 'product', 'prd', '需求', '产品'])
        is_deployment = any(kw in task_text for kw in ['deploy', 'release', 'ci/cd', '部署', '发布'])
        is_security = any(kw in task_text for kw in ['security', 'auth', 'vulnerability', '安全', '认证'])

        step_id = 1

        if is_product or is_architecture:
            steps.append(WorkflowStep(
                step_id=f"step_{step_id}", name="Requirements Analysis",
                description="Analyze task requirements and create detailed specification",
                role_id="product-manager", action="analyze_requirements",
            ))
            step_id += 1

        if is_architecture:
            steps.append(WorkflowStep(
                step_id=f"step_{step_id}", name="Architecture Design",
                description="Design system architecture and technology selection",
                role_id="architect", action="design_architecture",
            ))
            step_id += 1

        if is_security:
            steps.append(WorkflowStep(
                step_id=f"step_{step_id}", name="Security Review",
                description="Review security implications and recommend protections",
                role_id="security", action="security_review",
            ))
            step_id += 1

        if is_ui_design:
            steps.append(WorkflowStep(
                step_id=f"step_{step_id}", name="UI Design",
                description="Design user interface and interaction flow",
                role_id="ui-designer", action="design_ui",
            ))
            step_id += 1

        if is_testing:
            steps.append(WorkflowStep(
                step_id=f"step_{step_id}", name="Test Design",
                description="Create test strategy and test cases",
                role_id="tester", action="design_tests",
            ))
            step_id += 1

        if is_development:
            steps.append(WorkflowStep(
                step_id=f"step_{step_id}", name="Development",
                description="Implement feature code",
                role_id="solo-coder", action="develop",
            ))
            step_id += 1

        if is_testing and is_development:
            steps.append(WorkflowStep(
                step_id=f"step_{step_id}", name="Test Execution",
                description="Execute test cases and verify functionality",
                role_id="tester", action="execute_tests",
            ))
            step_id += 1

        if is_deployment:
            steps.append(WorkflowStep(
                step_id=f"step_{step_id}", name="Deployment",
                description="Deploy and release the system",
                role_id="devops", action="deploy",
            ))

        if not steps:
            steps.append(WorkflowStep(
                step_id="step_1", name="Task Execution",
                description=task_description or task_title,
                role_id=target_agent or "solo-coder", action="execute",
            ))

        return steps

    def start_workflow(self, workflow_id: str, variables: Dict[str, Any] = None) -> Optional[WorkflowInstance]:
        definition = self.definitions.get(workflow_id)
        if not definition:
            logger.warning("Workflow not found: %s", workflow_id)
            return None

        instance = WorkflowInstance(
            workflow_id=workflow_id,
            variables=variables or {},
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now().isoformat(),
        )

        if definition.steps:
            instance.current_step = definition.steps[0].step_id

        self.instances[instance.instance_id] = instance
        logger.info("Workflow started: %s", instance.instance_id)
        return instance

    def execute_step(self, instance_id: str, step_executor: Callable = None) -> Optional[WorkflowStep]:
        instance = self.instances.get(instance_id)
        if not instance:
            return None

        definition = self.definitions.get(instance.workflow_id)
        if not definition:
            return None

        current_step = None
        for step in definition.steps:
            if step.step_id == instance.current_step:
                current_step = step
                break

        if not current_step:
            return None

        current_step.status = StepStatus.RUNNING

        try:
            if step_executor:
                result = step_executor(current_step, instance.variables)
            elif current_step.action in self.executors:
                result = self.executors[current_step.action](current_step, instance.variables)
            else:
                result = self._default_step_executor(current_step, instance.variables)

            current_step.result = result
            current_step.status = StepStatus.COMPLETED
            instance.completed_steps.append(current_step.step_id)

            if len(instance.completed_steps) % self.checkpoint_interval == 0:
                self._save_checkpoint(instance, current_step)

            next_step = self._get_next_step(definition, current_step)
            if next_step:
                instance.current_step = next_step.step_id
            else:
                instance.status = WorkflowStatus.COMPLETED
                instance.completed_at = datetime.now().isoformat()

        except Exception as e:
            current_step.status = StepStatus.FAILED
            current_step.error = str(e)
            instance.failed_steps.append(current_step.step_id)
            instance.error = str(e)
            logger.warning("Step %s failed: %s", current_step.step_id, e)

        return current_step

    def _default_step_executor(self, step: WorkflowStep, variables: Dict[str, Any]) -> Any:
        if self.dispatcher:
            result = self.dispatcher.dispatch(
                task_description=step.description,
                roles=[step.role_id],
            )
            return {"dispatch_success": result.success, "summary": getattr(result, 'summary', '')[:200]}
        return {"action": step.action, "role": step.role_id, "status": "mock_completed"}

    def _get_next_step(self, definition: WorkflowDefinition, current_step: WorkflowStep) -> Optional[WorkflowStep]:
        found_current = False
        for step in definition.steps:
            if found_current:
                return step
            if step.step_id == current_step.step_id:
                found_current = True
        return None

    def _save_checkpoint(self, instance: WorkflowInstance, current_step: WorkflowStep):
        definition = self.definitions.get(instance.workflow_id)
        all_step_ids = [s.step_id for s in (definition.steps if definition else [])]
        remaining = [sid for sid in all_step_ids if sid not in instance.completed_steps and sid not in instance.failed_steps]

        checkpoint = self.checkpoint_manager.create_checkpoint_from_dispatch(
            task_id=instance.instance_id,
            step_name=current_step.name,
            agent_id=current_step.role_id,
            completed_steps=instance.completed_steps,
            remaining_steps=remaining,
            context=instance.variables,
            outputs=instance.results,
        )
        instance.checkpoint_id = checkpoint.checkpoint_id

    def resume_from_checkpoint(self, instance_id: str) -> Optional[WorkflowInstance]:
        instance = self.instances.get(instance_id)
        if not instance:
            return None

        if not instance.checkpoint_id:
            logger.warning("No checkpoint found for instance: %s", instance_id)
            return instance

        checkpoint = self.checkpoint_manager.load_checkpoint(instance.checkpoint_id)
        if not checkpoint:
            logger.warning("Failed to load checkpoint: %s", instance.checkpoint_id)
            return instance

        instance.completed_steps = checkpoint.completed_steps
        instance.variables = checkpoint.variables
        instance.results = checkpoint.outputs

        if checkpoint.remaining_steps:
            instance.current_step = checkpoint.remaining_steps[0]
            instance.status = WorkflowStatus.RUNNING
        else:
            instance.status = WorkflowStatus.COMPLETED

        logger.info("Resumed instance %s from checkpoint %s", instance_id, instance.checkpoint_id)
        return instance

    def handoff(self, instance_id: str, from_agent: str, to_agent: str, reason: str = "") -> Optional[HandoffDocument]:
        instance = self.instances.get(instance_id)
        if not instance:
            return None

        definition = self.definitions.get(instance.workflow_id)
        all_step_ids = [s.step_id for s in (definition.steps if definition else [])]
        remaining = [sid for sid in all_step_ids if sid not in instance.completed_steps]

        handoff = HandoffDocument(
            task_id=instance_id,
            from_agent=from_agent,
            to_agent=to_agent,
            completed_work=[f"Completed step: {sid}" for sid in instance.completed_steps],
            current_state=instance.variables,
            next_steps=remaining,
            handoff_reason=reason or "agent_handoff",
        )

        self.checkpoint_manager.save_handoff(handoff)
        instance.handoff_history.append(handoff.handoff_id)
        instance.current_agent_id = to_agent

        logger.info("Handoff: %s -> %s for instance %s", from_agent, to_agent, instance_id)
        return handoff

    def get_workflow_status(self, instance_id: str) -> Optional[Dict[str, Any]]:
        instance = self.instances.get(instance_id)
        if not instance:
            return None

        definition = self.definitions.get(instance.workflow_id)
        total_steps = len(definition.steps) if definition else 0
        completed = len(instance.completed_steps)
        failed = len(instance.failed_steps)

        return {
            'instance_id': instance_id,
            'workflow_id': instance.workflow_id,
            'status': instance.status.value,
            'progress': f"{completed}/{total_steps}",
            'completion_rate': (completed / total_steps * 100) if total_steps > 0 else 0,
            'current_step': instance.current_step,
            'failed_steps': instance.failed_steps,
            'has_checkpoint': instance.checkpoint_id is not None,
        }

    def register_executor(self, action: str, executor: Callable):
        self.executors[action] = executor
