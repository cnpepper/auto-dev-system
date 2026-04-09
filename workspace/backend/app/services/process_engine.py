"""
流程编排引擎

负责管理项目流程的状态机，协调各个阶段的执行
"""
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from sqlmodel import Session

from app.models import (
    Project,
    ProcessStage,
    ProcessStageCreate,
    FunctionModule,
    FunctionModuleCreate,
    ExecutionLog,
    ExecutionLogCreate,
    Error,
    ErrorCreate,
)
import app.crud_ai_programming as crud


class ProjectStatus(str, Enum):
    """项目状态枚举"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class StageStatus(str, Enum):
    """阶段状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class StageType(str, Enum):
    """阶段类型枚举"""
    DEVELOPING = "developing"
    TESTING = "testing"


class ProcessEngine:
    """
    流程编排引擎
    
    负责管理项目流程的状态机，协调各个阶段的执行
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def start_project(self, project_id: int) -> Project:
        """
        启动项目流程
        
        1. 更新项目状态为 running
        2. 创建初始开发阶段
        3. 触发文档扫描
        
        Args:
            project_id: 项目ID
            
        Returns:
            更新后的项目对象
        """
        project = crud.get_project(session=self.session, project_id=project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # 更新项目状态
        project.status = ProjectStatus.RUNNING.value
        project.started_at = datetime.now(timezone.utc)
        project.current_stage = "developing"
        self.session.add(project)
        self.session.commit()
        
        # 创建初始开发阶段
        stage_create = ProcessStageCreate(
            project_id=project_id,
            stage_type=StageType.DEVELOPING.value,
            stage_name="开发阶段-初始开发",
            status=StageStatus.PENDING.value,
        )
        stage = crud.create_process_stage(
            session=self.session,
            stage_create=stage_create,
        )
        
        # 记录日志
        self._log_info(
            stage_id=stage.id,
            message=f"项目 {project.name} 流程启动",
            extra_data={"project_id": project_id},
        )
        
        # TODO: 触发文档扫描任务
        
        return project
    
    def pause_project(self, project_id: int) -> Project:
        """
        暂停项目
        
        Args:
            project_id: 项目ID
            
        Returns:
            更新后的项目对象
        """
        project = crud.get_project(session=self.session, project_id=project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        if project.status != ProjectStatus.RUNNING.value:
            raise ValueError(f"Cannot pause project with status: {project.status}")
        
        # 更新项目状态
        project.status = ProjectStatus.PAUSED.value
        self.session.add(project)
        self.session.commit()
        
        # 记录日志
        current_stage = self._get_current_stage(project_id=project_id)
        if current_stage:
            self._log_info(
                stage_id=current_stage.id,
                message=f"项目 {project.name} 已暂停",
                extra_data={"project_id": project_id},
            )
        
        return project
    
    def resume_project(self, project_id: int) -> Project:
        """
        恢复项目
        
        Args:
            project_id: 项目ID
            
        Returns:
            更新后的项目对象
        """
        project = crud.get_project(session=self.session, project_id=project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        if project.status != ProjectStatus.PAUSED.value:
            raise ValueError(f"Cannot resume project with status: {project.status}")
        
        # 更新项目状态
        project.status = ProjectStatus.RUNNING.value
        self.session.add(project)
        self.session.commit()
        
        # 记录日志
        current_stage = self._get_current_stage(project_id=project_id)
        if current_stage:
            self._log_info(
                stage_id=current_stage.id,
                message=f"项目 {project.name} 已恢复",
                extra_data={"project_id": project_id},
            )
        
        # TODO: 触发流程继续执行
        
        return project
    
    def transition_stage(
        self,
        stage_id: int,
        new_status: StageStatus,
        error_message: Optional[str] = None,
    ) -> ProcessStage:
        """
        阶段状态转换
        
        Args:
            stage_id: 阶段ID
            new_status: 新状态
            error_message: 错误消息（如果失败）
            
        Returns:
            更新后的阶段对象
        """
        stage = crud.get_process_stage(session=self.session, stage_id=stage_id)
        if not stage:
            raise ValueError(f"Stage {stage_id} not found")
        
        old_status = stage.status
        stage.status = new_status.value
        
        # 更新时间戳
        if new_status == StageStatus.IN_PROGRESS:
            stage.started_at = datetime.now(timezone.utc)
        elif new_status in [StageStatus.COMPLETED, StageStatus.FAILED]:
            stage.completed_at = datetime.now(timezone.utc)
        
        self.session.add(stage)
        self.session.commit()
        
        # 记录日志
        self._log_info(
            stage_id=stage_id,
            message=f"阶段状态转换: {old_status} → {new_status.value}",
            extra_data={"old_status": old_status, "new_status": new_status.value},
        )
        
        # 如果阶段失败，记录错误
        if new_status == StageStatus.FAILED and error_message:
            self._create_error(
                project_id=stage.project_id,
                error_type="StageExecutionError",
                error_message=error_message,
                error_context={"stage_id": stage_id, "stage_name": stage.stage_name},
            )
        
        # 状态转换后的业务逻辑
        if new_status == StageStatus.COMPLETED:
            self._on_stage_completed(stage=stage)
        elif new_status == StageStatus.FAILED:
            self._on_stage_failed(stage=stage)
        elif new_status == StageStatus.APPROVED:
            self._on_stage_approved(stage=stage)
        elif new_status == StageStatus.REJECTED:
            self._on_stage_rejected(stage=stage)
        
        return stage
    
    def create_module(
        self,
        stage_id: int,
        module_name: str,
        description: Optional[str] = None,
    ) -> FunctionModule:
        """
        创建功能模块
        
        Args:
            stage_id: 阶段ID
            module_name: 模块名称
            description: 模块描述
            
        Returns:
            创建的功能模块对象
        """
        stage = crud.get_process_stage(session=self.session, stage_id=stage_id)
        if not stage:
            raise ValueError(f"Stage {stage_id} not found")
        
        module_create = FunctionModuleCreate(
            stage_id=stage_id,
            module_name=module_name,
            description=description,
            status=StageStatus.PENDING.value,
        )
        module = crud.create_function_module(
            session=self.session,
            module_create=module_create,
        )
        
        # 记录日志
        self._log_info(
            stage_id=stage_id,
            message=f"创建功能模块: {module_name}",
            extra_data={"module_id": module.id, "module_name": module_name},
        )
        
        return module
    
    def complete_module(self, module_id: int, git_commit_hash: str) -> FunctionModule:
        """
        完成功能模块开发
        
        Args:
            module_id: 模块ID
            git_commit_hash: Git提交哈希
            
        Returns:
            更新后的功能模块对象
        """
        module = crud.get_function_module(session=self.session, module_id=module_id)
        if not module:
            raise ValueError(f"Module {module_id} not found")
        
        from app.models import FunctionModuleUpdate
        update_data = FunctionModuleUpdate(
            status=StageStatus.COMPLETED.value,
            git_commit_hash=git_commit_hash,
            completed_at=datetime.now(timezone.utc),
        )
        module = crud.update_function_module(
            session=self.session,
            db_module=module,
            module_in=update_data,
        )
        
        # 记录日志
        self._log_info(
            stage_id=module.stage_id,
            message=f"功能模块开发完成: {module.module_name}",
            extra_data={
                "module_id": module_id,
                "git_commit_hash": git_commit_hash,
            },
        )
        
        return module
    
    # ==================== 私有方法 ====================
    
    def _get_current_stage(self, project_id: int) -> Optional[ProcessStage]:
        """获取当前活跃的阶段"""
        stages = crud.get_process_stages_by_project(
            session=self.session,
            project_id=project_id,
        )
        
        # 查找当前正在执行的阶段
        for stage in stages:
            if stage.status in [StageStatus.PENDING.value, StageStatus.IN_PROGRESS.value]:
                return stage
        
        return None
    
    def _on_stage_completed(self, stage: ProcessStage) -> None:
        """
        阶段完成后的处理
        
        Args:
            stage: 完成的阶段
        """
        # 如果是开发阶段，创建测试阶段
        if stage.stage_type == StageType.DEVELOPING.value:
            # 检查是否需要人工验收
            # TODO: 根据配置决定是否需要人工验收
            
            # 创建测试阶段
            test_stage_create = ProcessStageCreate(
                project_id=stage.project_id,
                stage_type=StageType.TESTING.value,
                stage_name="测试阶段",
                status=StageStatus.PENDING.value,
            )
            test_stage = crud.create_process_stage(
                session=self.session,
                stage_create=test_stage_create,
            )
            
            # 更新项目当前阶段
            project = crud.get_project(session=self.session, project_id=stage.project_id)
            if project:
                project.current_stage = "testing"
                self.session.add(project)
                self.session.commit()
        
        # 如果是测试阶段，检查是否所有测试通过
        elif stage.stage_type == StageType.TESTING.value:
            # TODO: 检查测试结果
            # 如果所有测试通过，标记项目完成
            pass
    
    def _on_stage_failed(self, stage: ProcessStage) -> None:
        """
        阶段失败后的处理
        
        Args:
            stage: 失败的阶段
        """
        # 更新项目状态为失败
        project = crud.get_project(session=self.session, project_id=stage.project_id)
        if project:
            project.status = ProjectStatus.FAILED.value
            self.session.add(project)
            self.session.commit()
            
            # 记录日志
            self._log_error(
                stage_id=stage.id,
                message=f"项目 {project.name} 执行失败",
                extra_data={"project_id": project.id},
            )
    
    def _on_stage_approved(self, stage: ProcessStage) -> None:
        """
        阶段审批通过后的处理
        
        Args:
            stage: 审批通过的阶段
        """
        # 标记阶段为已完成
        self.transition_stage(
            stage_id=stage.id,
            new_status=StageStatus.COMPLETED,
        )
    
    def _on_stage_rejected(self, stage: ProcessStage) -> None:
        """
        阶段审批拒绝后的处理
        
        Args:
            stage: 审批拒绝的阶段
        """
        # TODO: 实现回退逻辑
        # 根据配置决定是否回退到上一个阶段
        
        # 记录日志
        self._log_warning(
            stage_id=stage.id,
            message=f"阶段 {stage.stage_name} 审批被拒绝，需要修改",
            extra_data={"stage_id": stage.id},
        )
    
    def _log_info(self, stage_id: int, message: str, extra_data: Optional[dict] = None) -> None:
        """记录INFO日志"""
        log_create = ExecutionLogCreate(
            stage_id=stage_id,
            log_level="INFO",
            message=message,
            extra_data=extra_data,
        )
        crud.create_execution_log(session=self.session, log_create=log_create)
    
    def _log_error(self, stage_id: int, message: str, extra_data: Optional[dict] = None) -> None:
        """记录ERROR日志"""
        log_create = ExecutionLogCreate(
            stage_id=stage_id,
            log_level="ERROR",
            message=message,
            extra_data=extra_data,
        )
        crud.create_execution_log(session=self.session, log_create=log_create)
    
    def _log_warning(self, stage_id: int, message: str, extra_data: Optional[dict] = None) -> None:
        """记录WARNING日志"""
        log_create = ExecutionLogCreate(
            stage_id=stage_id,
            log_level="WARNING",
            message=message,
            extra_data=extra_data,
        )
        crud.create_execution_log(session=self.session, log_create=log_create)
    
    def _create_error(
        self,
        project_id: int,
        error_type: str,
        error_message: str,
        error_context: Optional[dict] = None,
    ) -> Error:
        """创建错误记录"""
        error_create = ErrorCreate(
            project_id=project_id,
            error_type=error_type,
            error_message=error_message,
            error_context=error_context,
        )
        return crud.create_error(session=self.session, error_create=error_create)
