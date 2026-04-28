#!/usr/bin/env python3
import json
import logging
import hashlib
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class CheckpointStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class Checkpoint:
    checkpoint_id: str = field(default_factory=lambda: f"cp-{uuid.uuid4().hex[:8]}")
    task_id: str = ""
    step_id: str = ""
    step_name: str = ""
    agent_id: str = ""
    status: CheckpointStatus = CheckpointStatus.ACTIVE
    completed_steps: List[str] = field(default_factory=list)
    remaining_steps: List[str] = field(default_factory=list)
    progress_percentage: float = 0.0
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None
    checkpoint_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
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
            'checkpoint_hash': self.checkpoint_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checkpoint':
        data_copy = dict(data)
        if isinstance(data_copy.get('status'), str):
            try:
                data_copy['status'] = CheckpointStatus(data_copy['status'])
            except ValueError:
                data_copy['status'] = CheckpointStatus.ACTIVE
        return cls(**data_copy)


@dataclass
class HandoffDocument:
    handoff_id: str = field(default_factory=lambda: f"hoff-{uuid.uuid4().hex[:8]}")
    task_id: str = ""
    from_agent: str = ""
    to_agent: str = ""
    completed_work: List[str] = field(default_factory=list)
    current_state: Dict[str, Any] = field(default_factory=dict)
    next_steps: List[str] = field(default_factory=list)
    pending_issues: List[str] = field(default_factory=list)
    important_notes: List[str] = field(default_factory=list)
    context_for_next: Dict[str, Any] = field(default_factory=dict)
    accumulated_knowledge: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    handoff_reason: str = "task_completed"
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HandoffDocument':
        return cls(**data)

    def to_markdown(self) -> str:
        md = f"# Task Handoff Document\n\n"
        md += f"## Basic Info\n"
        md += f"- **Handoff ID**: {self.handoff_id}\n"
        md += f"- **Task ID**: {self.task_id}\n"
        md += f"- **Time**: {self.created_at}\n"
        md += f"- **Reason**: {self.handoff_reason}\n"
        md += f"- **Confidence**: {self.confidence:.0%}\n\n"
        md += f"## From -> To\n"
        md += f"- **From**: {self.from_agent}\n"
        md += f"- **To**: {self.to_agent}\n\n---\n\n"
        md += f"## Completed Work\n"
        for i, work in enumerate(self.completed_work, 1):
            md += f"{i}. {work}\n"
        md += f"\n## Current State\n\n```json\n{json.dumps(self.current_state, indent=2, ensure_ascii=False)}\n```\n"
        md += f"\n## Next Steps\n"
        for i, step in enumerate(self.next_steps, 1):
            md += f"{i}. {step}\n"
        if self.pending_issues:
            md += f"\n## Pending Issues\n"
            for i, issue in enumerate(self.pending_issues, 1):
                md += f"{i}. {issue}\n"
        if self.important_notes:
            md += f"\n## Important Notes\n"
            for note in self.important_notes:
                md += f"- {note}\n"
        return md


class CheckpointManager:
    """
    Checkpoint manager for long-running task state persistence.

    Features:
    1. Periodic task state saving (like git commits)
    2. Recovery from any checkpoint
    3. Automatic handoff document generation
    4. Data integrity verification (SHA256)
    5. Expired checkpoint auto-cleanup
    """

    def __init__(self, storage_path: str = "./checkpoints"):
        self.storage_path = Path(storage_path)
        self.checkpoints_dir = self.storage_path / "checkpoints"
        self.handoffs_dir = self.storage_path / "handoffs"
        self._ensure_directories()

    def _ensure_directories(self):
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.handoffs_dir.mkdir(parents=True, exist_ok=True)

    def _compute_hash(self, data: Dict[str, Any]) -> str:
        data_for_hash = {k: v for k, v in data.items() if k != 'checkpoint_hash'}
        json_str = json.dumps(data_for_hash, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    def _validate_id(self, id_str: str) -> None:
        if '..' in id_str or '/' in id_str or '\\' in id_str:
            raise ValueError(f"Invalid ID (path traversal detected): {id_str}")

    def _get_checkpoint_path(self, checkpoint_id: str) -> Path:
        self._validate_id(checkpoint_id)
        path = self.checkpoints_dir / f"{checkpoint_id}.json"
        if not path.resolve().is_relative_to(self.checkpoints_dir.resolve()):
            raise ValueError(f"Path traversal detected: {checkpoint_id}")
        return path

    def _get_handoff_path(self, handoff_id: str) -> Path:
        self._validate_id(handoff_id)
        path = self.handoffs_dir / f"{handoff_id}.json"
        if not path.resolve().is_relative_to(self.handoffs_dir.resolve()):
            raise ValueError(f"Path traversal detected: {handoff_id}")
        return path

    def save_checkpoint(self, checkpoint: Checkpoint) -> bool:
        try:
            checkpoint.updated_at = datetime.now().isoformat()
            checkpoint_dict = checkpoint.to_dict()
            checkpoint.checkpoint_hash = self._compute_hash(checkpoint_dict)
            checkpoint_dict['checkpoint_hash'] = checkpoint.checkpoint_hash

            checkpoint_path = self._get_checkpoint_path(checkpoint.checkpoint_id)
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_dict, f, indent=2, ensure_ascii=False)

            logger.info("Checkpoint saved: %s (%.1f%%)", checkpoint.checkpoint_id, checkpoint.progress_percentage)
            return True
        except Exception as e:
            logger.warning("Failed to save checkpoint: %s", e)
            return False

    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        try:
            checkpoint_path = self._get_checkpoint_path(checkpoint_id)
            if not checkpoint_path.exists():
                logger.warning("Checkpoint not found: %s", checkpoint_id)
                return None

            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            checkpoint = Checkpoint.from_dict(data)
            computed_hash = self._compute_hash({k: v for k, v in data.items() if k != 'checkpoint_hash'})
            if computed_hash != checkpoint.checkpoint_hash:
                logger.warning("Checkpoint integrity check failed: %s", checkpoint_id)
                return None

            return checkpoint
        except Exception as e:
            logger.warning("Failed to load checkpoint: %s", e)
            return None

    def get_latest_checkpoint(self, task_id: str) -> Optional[Checkpoint]:
        try:
            task_checkpoints = []
            for cp_path in self.checkpoints_dir.glob("*.json"):
                with open(cp_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('task_id') == task_id:
                        task_checkpoints.append((cp_path.stat().st_mtime, Checkpoint.from_dict(data)))

            if not task_checkpoints:
                return None

            latest = sorted(task_checkpoints, key=lambda x: x[0], reverse=True)[0][1]
            return latest
        except Exception as e:
            logger.warning("Failed to get latest checkpoint: %s", e)
            return None

    def list_checkpoints(self, task_id: Optional[str] = None) -> List[Checkpoint]:
        try:
            checkpoints = []
            for cp_path in self.checkpoints_dir.glob("*.json"):
                with open(cp_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if task_id is None or data.get('task_id') == task_id:
                        checkpoints.append(Checkpoint.from_dict(data))
            checkpoints.sort(key=lambda x: x.created_at, reverse=True)
            return checkpoints
        except Exception as e:
            logger.warning("Failed to list checkpoints: %s", e)
            return []

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        try:
            checkpoint_path = self._get_checkpoint_path(checkpoint_id)
            if checkpoint_path.exists():
                checkpoint_path.unlink()
                return True
            return False
        except Exception as e:
            logger.warning("Failed to delete checkpoint: %s", e)
            return False

    def cleanup_expired_checkpoints(self, max_age_hours: int = 24) -> int:
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            cleaned_count = 0
            for cp_path in self.checkpoints_dir.glob("*.json"):
                if cp_path.stat().st_mtime < cutoff_time.timestamp():
                    cp_path.unlink()
                    cleaned_count += 1
            if cleaned_count > 0:
                logger.info("Cleaned %d expired checkpoints", cleaned_count)
            return cleaned_count
        except Exception as e:
            logger.warning("Failed to cleanup expired checkpoints: %s", e)
            return 0

    def save_handoff(self, handoff: HandoffDocument) -> bool:
        try:
            handoff_path = self._get_handoff_path(handoff.handoff_id)
            with open(handoff_path, 'w', encoding='utf-8') as f:
                json.dump(handoff.to_dict(), f, indent=2, ensure_ascii=False)

            md_path = handoff_path.with_suffix('.md')
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(handoff.to_markdown())

            logger.info("Handoff saved: %s -> %s", handoff.from_agent, handoff.to_agent)
            return True
        except Exception as e:
            logger.warning("Failed to save handoff: %s", e)
            return False

    def load_handoff(self, handoff_id: str) -> Optional[HandoffDocument]:
        try:
            handoff_path = self._get_handoff_path(handoff_id)
            if not handoff_path.exists():
                return None
            with open(handoff_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return HandoffDocument.from_dict(data)
        except Exception as e:
            logger.warning("Failed to load handoff: %s", e)
            return None

    def get_task_handoffs(self, task_id: str) -> List[HandoffDocument]:
        try:
            handoffs = []
            for hf_path in self.handoffs_dir.glob("*.json"):
                with open(hf_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('task_id') == task_id:
                        handoffs.append(HandoffDocument.from_dict(data))
            handoffs.sort(key=lambda x: x.created_at)
            return handoffs
        except Exception as e:
            logger.warning("Failed to get task handoffs: %s", e)
            return []

    def create_checkpoint_from_dispatch(
        self,
        task_id: str,
        step_name: str,
        agent_id: str,
        completed_steps: List[str],
        remaining_steps: List[str],
        context: Dict[str, Any] = None,
        outputs: Dict[str, Any] = None,
    ) -> Checkpoint:
        total = len(completed_steps) + len(remaining_steps)
        progress = len(completed_steps) / total if total > 0 else 0.0

        checkpoint = Checkpoint(
            task_id=task_id,
            step_id=f"step-{len(completed_steps)+1}",
            step_name=step_name,
            agent_id=agent_id,
            status=CheckpointStatus.ACTIVE,
            completed_steps=completed_steps,
            remaining_steps=remaining_steps,
            progress_percentage=progress,
            context_snapshot=context or {},
            outputs=outputs or {},
        )
        self.save_checkpoint(checkpoint)
        return checkpoint
