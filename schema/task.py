from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class TaskPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskType(str, Enum):
    CODE_GENERATION = "code_generation"
    CODE_EXECUTION = "code_execution"
    FILE_OPERATION = "file_operation"
    SHELL_COMMAND = "shell_command"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    REVIEW = "review"
    EVOLUTION = "evolution"


class IntentType(str, Enum):
    CODE_WRITE = "code_write"
    CODE_READ = "code_read"
    CODE_MODIFY = "code_modify"
    CODE_EXECUTE = "code_execute"
    FILE_SEARCH = "file_search"
    FILE_CREATE = "file_create"
    FILE_DELETE = "file_delete"
    SHELL_RUN = "shell_run"
    PROJECT_PLAN = "project_plan"
    CODE_REVIEW = "code_review"
    QUESTION = "question"
    UNKNOWN = "unknown"


class Task(BaseModel):
    id: str = Field(default_factory=lambda: f"task_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    description: str
    task_type: TaskType = TaskType.CODE_GENERATION
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 3
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def mark_in_progress(self):
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now()

    def mark_completed(self, result: str):
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.updated_at = datetime.now()

    def mark_failed(self, error: str):
        self.status = TaskStatus.FAILED
        self.error = error
        self.attempts += 1
        self.updated_at = datetime.now()

    def can_retry(self) -> bool:
        return self.attempts < self.max_attempts


class TaskPlan(BaseModel):
    user_request: str
    intent: IntentType = IntentType.UNKNOWN
    tasks: List[Task] = Field(default_factory=list)
    current_task_index: int = 0
    status: str = "planned"
    created_at: datetime = Field(default_factory=datetime.now)

    def get_current_task(self) -> Optional[Task]:
        if self.current_task_index < len(self.tasks):
            return self.tasks[self.current_task_index]
        return None

    def advance(self) -> Optional[Task]:
        self.current_task_index += 1
        return self.get_current_task()

    def add_task(self, task: Task, position: Optional[int] = None):
        if position is not None:
            self.tasks.insert(position, task)
        else:
            self.tasks.append(task)

    def is_completed(self) -> bool:
        return all(t.status == TaskStatus.COMPLETED for t in self.tasks)


class ExecutionResult(BaseModel):
    success: bool
    output: str = ""
    error: str = ""
    code: str = ""
    execution_time: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AuditResult(BaseModel):
    status: str
    feedback: str
    suggestions: List[str] = Field(default_factory=list)
    score: Optional[int] = None


class IntentRecognitionResult(BaseModel):
    intent: IntentType
    confidence: float
    entities: Dict[str, Any] = Field(default_factory=dict)
    suggested_tasks: List[TaskType] = Field(default_factory=list)
