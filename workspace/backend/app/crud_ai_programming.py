"""
AI编程系统CRUD操作
"""
from typing import Any
from sqlmodel import Session, select

from app.models import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProcessStage,
    ProcessStageCreate,
    ProcessStageUpdate,
    FunctionModule,
    FunctionModuleCreate,
    FunctionModuleUpdate,
    TestCase,
    TestCaseCreate,
    TestCaseUpdate,
    TestReport,
    TestReportCreate,
    ExecutionLog,
    ExecutionLogCreate,
    Document,
    DocumentCreate,
    DocumentUpdate,
    SystemConfig,
    SystemConfigCreate,
    SystemConfigUpdate,
    ToolConfig,
    ToolConfigCreate,
    ToolConfigUpdate,
    Session as SessionModel,
    SessionCreate,
    SessionUpdate,
    Error,
    ErrorCreate,
    ErrorUpdate,
)


# ==================== 项目CRUD ====================

def create_project(*, session: Session, project_create: ProjectCreate) -> Project:
    """创建新项目"""
    db_obj = Project.model_validate(project_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_project(*, session: Session, project_id: int) -> Project | None:
    """获取单个项目"""
    return session.get(Project, project_id)


def get_projects(*, session: Session, skip: int = 0, limit: int = 100) -> list[Project]:
    """获取项目列表"""
    statement = select(Project).offset(skip).limit(limit).order_by(Project.created_at.desc())
    return list(session.exec(statement).all())


def count_projects(*, session: Session) -> int:
    """统计项目总数"""
    statement = select(Project)
    return len(list(session.exec(statement).all()))


def update_project(*, session: Session, db_project: Project, project_in: ProjectUpdate) -> Project:
    """更新项目"""
    project_data = project_in.model_dump(exclude_unset=True)
    db_project.sqlmodel_update(project_data)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project


def delete_project(*, session: Session, project_id: int) -> bool:
    """删除项目"""
    project = session.get(Project, project_id)
    if project:
        session.delete(project)
        session.commit()
        return True
    return False


# ==================== 流程阶段CRUD ====================

def create_process_stage(*, session: Session, stage_create: ProcessStageCreate) -> ProcessStage:
    """创建流程阶段"""
    db_obj = ProcessStage.model_validate(stage_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_process_stage(*, session: Session, stage_id: int) -> ProcessStage | None:
    """获取单个流程阶段"""
    return session.get(ProcessStage, stage_id)


def get_process_stages_by_project(*, session: Session, project_id: int) -> list[ProcessStage]:
    """获取项目的所有流程阶段"""
    statement = (
        select(ProcessStage)
        .where(ProcessStage.project_id == project_id)
        .order_by(ProcessStage.created_at)
    )
    return list(session.exec(statement).all())


def update_process_stage(*, session: Session, db_stage: ProcessStage, stage_in: ProcessStageUpdate) -> ProcessStage:
    """更新流程阶段"""
    stage_data = stage_in.model_dump(exclude_unset=True)
    db_stage.sqlmodel_update(stage_data)
    session.add(db_stage)
    session.commit()
    session.refresh(db_stage)
    return db_stage


# ==================== 功能模块CRUD ====================

def create_function_module(*, session: Session, module_create: FunctionModuleCreate) -> FunctionModule:
    """创建功能模块"""
    db_obj = FunctionModule.model_validate(module_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_function_module(*, session: Session, module_id: int) -> FunctionModule | None:
    """获取单个功能模块"""
    return session.get(FunctionModule, module_id)


def get_function_modules_by_stage(*, session: Session, stage_id: int) -> list[FunctionModule]:
    """获取阶段的所有功能模块"""
    statement = (
        select(FunctionModule)
        .where(FunctionModule.stage_id == stage_id)
        .order_by(FunctionModule.created_at)
    )
    return list(session.exec(statement).all())


def update_function_module(*, session: Session, db_module: FunctionModule, module_in: FunctionModuleUpdate) -> FunctionModule:
    """更新功能模块"""
    module_data = module_in.model_dump(exclude_unset=True)
    db_module.sqlmodel_update(module_data)
    session.add(db_module)
    session.commit()
    session.refresh(db_module)
    return db_module


# ==================== 测试用例CRUD ====================

def create_test_case(*, session: Session, test_create: TestCaseCreate) -> TestCase:
    """创建测试用例"""
    db_obj = TestCase.model_validate(test_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_test_cases_by_module(*, session: Session, module_id: int) -> list[TestCase]:
    """获取模块的所有测试用例"""
    statement = (
        select(TestCase)
        .where(TestCase.module_id == module_id)
        .order_by(TestCase.created_at)
    )
    return list(session.exec(statement).all())


def update_test_case(*, session: Session, db_test: TestCase, test_in: TestCaseUpdate) -> TestCase:
    """更新测试用例"""
    test_data = test_in.model_dump(exclude_unset=True)
    db_test.sqlmodel_update(test_data)
    session.add(db_test)
    session.commit()
    session.refresh(db_test)
    return db_test


# ==================== 测试报告CRUD ====================

def create_test_report(*, session: Session, report_create: TestReportCreate) -> TestReport:
    """创建测试报告"""
    db_obj = TestReport.model_validate(report_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_test_reports_by_stage(*, session: Session, stage_id: int) -> list[TestReport]:
    """获取阶段的所有测试报告"""
    statement = (
        select(TestReport)
        .where(TestReport.stage_id == stage_id)
        .order_by(TestReport.created_at.desc())
    )
    return list(session.exec(statement).all())


# ==================== 执行日志CRUD ====================

def create_execution_log(*, session: Session, log_create: ExecutionLogCreate) -> ExecutionLog:
    """创建执行日志"""
    db_obj = ExecutionLog.model_validate(log_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_execution_logs_by_stage(*, session: Session, stage_id: int, skip: int = 0, limit: int = 100) -> list[ExecutionLog]:
    """获取阶段的执行日志(分页)"""
    statement = (
        select(ExecutionLog)
        .where(ExecutionLog.stage_id == stage_id)
        .order_by(ExecutionLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def count_execution_logs_by_stage(*, session: Session, stage_id: int) -> int:
    """统计阶段的执行日志数量"""
    statement = select(ExecutionLog).where(ExecutionLog.stage_id == stage_id)
    return len(list(session.exec(statement).all()))


# ==================== 文档CRUD ====================

def create_document(*, session: Session, doc_create: DocumentCreate) -> Document:
    """创建文档"""
    db_obj = Document.model_validate(doc_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_documents_by_project(*, session: Session, project_id: int) -> list[Document]:
    """获取项目的所有文档"""
    statement = (
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.created_at)
    )
    return list(session.exec(statement).all())


def update_document(*, session: Session, db_doc: Document, doc_in: DocumentUpdate) -> Document:
    """更新文档"""
    doc_data = doc_in.model_dump(exclude_unset=True)
    db_doc.sqlmodel_update(doc_data)
    session.add(db_doc)
    session.commit()
    session.refresh(db_doc)
    return db_doc


# ==================== 系统配置CRUD ====================

def create_system_config(*, session: Session, config_create: SystemConfigCreate) -> SystemConfig:
    """创建系统配置"""
    db_obj = SystemConfig.model_validate(config_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_system_config(*, session: Session, config_id: int) -> SystemConfig | None:
    """获取单个系统配置"""
    return session.get(SystemConfig, config_id)


def get_system_config_by_key(*, session: Session, config_key: str) -> SystemConfig | None:
    """根据key获取系统配置"""
    statement = select(SystemConfig).where(SystemConfig.config_key == config_key)
    return session.exec(statement).first()


def get_system_configs(*, session: Session) -> list[SystemConfig]:
    """获取所有系统配置"""
    statement = select(SystemConfig).order_by(SystemConfig.config_key)
    return list(session.exec(statement).all())


def update_system_config(*, session: Session, db_config: SystemConfig, config_in: SystemConfigUpdate) -> SystemConfig:
    """更新系统配置"""
    config_data = config_in.model_dump(exclude_unset=True)
    db_config.sqlmodel_update(config_data)
    session.add(db_config)
    session.commit()
    session.refresh(db_config)
    return db_config


# ==================== 工具配置CRUD ====================

def create_tool_config(*, session: Session, tool_create: ToolConfigCreate) -> ToolConfig:
    """创建工具配置"""
    db_obj = ToolConfig.model_validate(tool_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_tool_config(*, session: Session, tool_id: int) -> ToolConfig | None:
    """获取单个工具配置"""
    return session.get(ToolConfig, tool_id)


def get_tool_configs(*, session: Session) -> list[ToolConfig]:
    """获取所有工具配置"""
    statement = select(ToolConfig).order_by(ToolConfig.tool_name)
    return list(session.exec(statement).all())


def update_tool_config(*, session: Session, db_tool: ToolConfig, tool_in: ToolConfigUpdate) -> ToolConfig:
    """更新工具配置"""
    tool_data = tool_in.model_dump(exclude_unset=True)
    db_tool.sqlmodel_update(tool_data)
    session.add(db_tool)
    session.commit()
    session.refresh(db_tool)
    return db_tool


# ==================== 会话CRUD ====================

def create_session(*, session: Session, session_create: SessionCreate) -> SessionModel:
    """创建会话"""
    db_obj = SessionModel.model_validate(session_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_session(*, session: Session, session_id: int) -> SessionModel | None:
    """获取单个会话"""
    return session.get(SessionModel, session_id)


def get_session_by_sdk_id(*, session: Session, sdk_session_id: str) -> SessionModel | None:
    """根据SDK会话ID获取会话"""
    statement = select(SessionModel).where(SessionModel.session_id == sdk_session_id)
    return session.exec(statement).first()


def get_sessions_by_project(*, session: Session, project_id: int) -> list[SessionModel]:
    """获取项目的所有会话"""
    statement = (
        select(SessionModel)
        .where(SessionModel.project_id == project_id)
        .order_by(SessionModel.created_at.desc())
    )
    return list(session.exec(statement).all())


def update_session(*, session: Session, db_session: SessionModel, session_in: SessionUpdate) -> SessionModel:
    """更新会话"""
    session_data = session_in.model_dump(exclude_unset=True)
    db_session.sqlmodel_update(session_data)
    session.add(db_session)
    session.commit()
    session.refresh(db_session)
    return db_session


# ==================== 错误记录CRUD ====================

def create_error(*, session: Session, error_create: ErrorCreate) -> Error:
    """创建错误记录"""
    db_obj = Error.model_validate(error_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_errors_by_project(*, session: Session, project_id: int) -> list[Error]:
    """获取项目的所有错误记录"""
    statement = (
        select(Error)
        .where(Error.project_id == project_id)
        .order_by(Error.created_at.desc())
    )
    return list(session.exec(statement).all())


def update_error(*, session: Session, db_error: Error, error_in: ErrorUpdate) -> Error:
    """更新错误记录"""
    error_data = error_in.model_dump(exclude_unset=True)
    db_error.sqlmodel_update(error_data)
    session.add(db_error)
    session.commit()
    session.refresh(db_error)
    return db_error
