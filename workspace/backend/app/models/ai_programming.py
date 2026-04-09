"""
自动化AI编程系统数据模型

包含以下核心实体：
- Project: 项目
- ProcessStage: 流程阶段
- FunctionModule: 功能模块
- TestCase: 测试用例
- TestReport: 测试报告
- ExecutionLog: 执行日志
- Document: 文档
- SystemConfig: 系统配置
- ToolConfig: 工具配置
- Session: 会话
- Error: 错误记录
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    """获取UTC时间"""
    from datetime import timezone
    return datetime.now(timezone.utc)


# ==================== 项目模型 ====================

class ProjectBase(SQLModel):
    """项目基础模型"""
    name: str = Field(max_length=255, description="项目名称")
    description: Optional[str] = Field(default=None, description="项目描述")
    current_stage: str = Field(default="idle", max_length=50, description="当前阶段")
    current_module: Optional[str] = Field(default=None, max_length=255, description="当前功能模块名称")
    status: str = Field(default="idle", max_length=50, description="项目状态")
    input_document_dir: str = Field(default="./input_docs", max_length=500, description="文档输入目录路径")
    project_path: str = Field(default="./projects", max_length=500, description="项目代码路径")
    requirements: Optional[str] = Field(default=None, description="项目需求")
    tech_stack: Optional[str] = Field(default=None, description="技术栈")
    current_session_id: Optional[str] = Field(default=None, max_length=100, description="当前活跃的会话ID")


class Project(ProjectBase, table=True):
    """项目表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    started_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        description="项目启动时间"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        description="项目完成时间"
    )
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="更新时间"
    )
    
    # 关系
    stages: list["ProcessStage"] = Relationship(back_populates="project", cascade_delete=True)
    documents: list["Document"] = Relationship(back_populates="project", cascade_delete=True)
    sessions: list["Session"] = Relationship(back_populates="project", cascade_delete=True)
    errors: list["Error"] = Relationship(back_populates="project", cascade_delete=True)


class ProjectCreate(ProjectBase):
    """创建项目Schema"""
    pass


class ProjectUpdate(SQLModel):
    """更新项目Schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    current_stage: Optional[str] = None
    current_module: Optional[str] = None
    status: Optional[str] = None
    input_document_dir: Optional[str] = None
    project_path: Optional[str] = None
    current_session_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ProjectPublic(ProjectBase):
    """项目公开Schema"""
    id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ==================== 流程阶段模型 ====================

class ProcessStageBase(SQLModel):
    """流程阶段基础模型"""
    stage_type: str = Field(max_length=50, description="阶段类型: developing/testing")
    stage_name: str = Field(max_length=255, description="阶段名称")
    status: str = Field(default="pending", max_length=50, description="状态")


class ProcessStage(ProcessStageBase, table=True):
    """流程阶段表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", nullable=False, ondelete="CASCADE")
    started_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        description="开始时间"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        description="完成时间"
    )
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="更新时间"
    )
    
    # 关系
    project: Optional[Project] = Relationship(back_populates="stages")
    modules: list["FunctionModule"] = Relationship(back_populates="stage", cascade_delete=True)
    logs: list["ExecutionLog"] = Relationship(back_populates="stage", cascade_delete=True)
    test_reports: list["TestReport"] = Relationship(back_populates="stage", cascade_delete=True)


class ProcessStageCreate(ProcessStageBase):
    """创建流程阶段Schema"""
    project_id: int


class ProcessStageUpdate(SQLModel):
    """更新流程阶段Schema"""
    stage_type: Optional[str] = None
    stage_name: Optional[str] = None
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ProcessStagePublic(ProcessStageBase):
    """流程阶段公开Schema"""
    id: int
    project_id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ==================== 功能模块模型 ====================

class FunctionModuleBase(SQLModel):
    """功能模块基础模型"""
    module_name: str = Field(max_length=255, description="模块名称")
    description: Optional[str] = Field(default=None, description="模块描述")
    status: str = Field(default="pending", max_length=50, description="状态")
    git_commit_hash: Optional[str] = Field(default=None, max_length=40, description="Git提交哈希")


class FunctionModule(FunctionModuleBase, table=True):
    """功能模块表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    stage_id: int = Field(foreign_key="processstage.id", nullable=False, ondelete="CASCADE")
    started_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        description="开始时间"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        description="完成时间"
    )
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="更新时间"
    )
    
    # 关系
    stage: Optional[ProcessStage] = Relationship(back_populates="modules")
    test_cases: list["TestCase"] = Relationship(back_populates="module", cascade_delete=True)


class FunctionModuleCreate(FunctionModuleBase):
    """创建功能模块Schema"""
    stage_id: int


class FunctionModuleUpdate(SQLModel):
    """更新功能模块Schema"""
    module_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    git_commit_hash: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class FunctionModulePublic(FunctionModuleBase):
    """功能模块公开Schema"""
    id: int
    stage_id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ==================== 测试用例模型 ====================

class TestCaseBase(SQLModel):
    """测试用例基础模型"""
    test_name: str = Field(max_length=255, description="测试用例名称")
    test_type: str = Field(max_length=50, description="测试类型: positive/negative/exception")
    status: str = Field(default="pending", max_length=50, description="状态")
    error_message: Optional[str] = Field(default=None, description="错误信息")


class TestCase(TestCaseBase, table=True):
    """测试用例表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    module_id: int = Field(foreign_key="functionmodule.id", nullable=False, ondelete="CASCADE")
    started_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        description="开始时间"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        description="完成时间"
    )
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="更新时间"
    )
    
    # 关系
    module: Optional[FunctionModule] = Relationship(back_populates="test_cases")


class TestCaseCreate(TestCaseBase):
    """创建测试用例Schema"""
    module_id: int


class TestCaseUpdate(SQLModel):
    """更新测试用例Schema"""
    test_name: Optional[str] = None
    test_type: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TestCasePublic(TestCaseBase):
    """测试用例公开Schema"""
    id: int
    module_id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ==================== 测试报告模型 ====================

class TestReportBase(SQLModel):
    """测试报告基础模型"""
    report_file_path: str = Field(max_length=500, description="报告文件路径")
    total_cases: int = Field(default=0, description="总测试用例数")
    passed_cases: int = Field(default=0, description="通过用例数")
    failed_cases: int = Field(default=0, description="失败用例数")
    status: str = Field(default="pending", max_length=50, description="报告状态")


class TestReport(TestReportBase, table=True):
    """测试报告表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    stage_id: int = Field(foreign_key="processstage.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="创建时间"
    )
    
    # 关系
    stage: Optional[ProcessStage] = Relationship(back_populates="test_reports")


class TestReportCreate(TestReportBase):
    """创建测试报告Schema"""
    stage_id: int


class TestReportPublic(TestReportBase):
    """测试报告公开Schema"""
    id: int
    stage_id: int
    created_at: datetime


# ==================== 执行日志模型 ====================

class ExecutionLogBase(SQLModel):
    """执行日志基础模型"""
    log_level: str = Field(default="INFO", max_length=20, description="日志级别")
    message: str = Field(description="日志消息")
    extra_data: Optional[dict] = Field(default=None, sa_type=JSON, description="额外元数据")


class ExecutionLog(ExecutionLogBase, table=True):
    """执行日志表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    stage_id: int = Field(foreign_key="processstage.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="创建时间"
    )
    
    # 关系
    stage: Optional[ProcessStage] = Relationship(back_populates="logs")


class ExecutionLogCreate(ExecutionLogBase):
    """创建执行日志Schema"""
    stage_id: int


class ExecutionLogPublic(ExecutionLogBase):
    """执行日志公开Schema"""
    id: int
    stage_id: int
    created_at: datetime


# ==================== 文档模型 ====================

class DocumentBase(SQLModel):
    """文档基础模型"""
    doc_type: str = Field(max_length=50, description="文档类型: prd/design/prototype/test_report")
    file_path: str = Field(max_length=500, description="文档文件路径")
    file_name: str = Field(max_length=255, description="文档文件名")
    status: str = Field(default="pending", max_length=50, description="状态")


class Document(DocumentBase, table=True):
    """文档表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", nullable=False, ondelete="CASCADE")
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="更新时间"
    )
    
    # 关系
    project: Optional[Project] = Relationship(back_populates="documents")


class DocumentCreate(DocumentBase):
    """创建文档Schema"""
    project_id: int


class DocumentUpdate(SQLModel):
    """更新文档Schema"""
    doc_type: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    status: Optional[str] = None


class DocumentPublic(DocumentBase):
    """文档公开Schema"""
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime


# ==================== 系统配置模型 ====================

class SystemConfigBase(SQLModel):
    """系统配置基础模型"""
    config_key: str = Field(max_length=100, unique=True, description="配置键")
    config_value: str = Field(description="配置值")
    description: Optional[str] = Field(default=None, description="配置说明")


class SystemConfig(SystemConfigBase, table=True):
    """系统配置表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="更新时间"
    )


class SystemConfigCreate(SystemConfigBase):
    """创建系统配置Schema"""
    pass


class SystemConfigUpdate(SQLModel):
    """更新系统配置Schema"""
    config_value: str
    description: Optional[str] = None


class SystemConfigPublic(SystemConfigBase):
    """系统配置公开Schema"""
    id: int
    created_at: datetime
    updated_at: datetime


# ==================== 工具配置模型 ====================

class ToolConfigBase(SQLModel):
    """工具配置基础模型"""
    tool_name: str = Field(max_length=100, unique=True, description="工具名称")
    tool_type: str = Field(max_length=50, description="工具类型")
    config_json: dict = Field(sa_type=JSON, description="工具配置JSON")
    is_active: bool = Field(default=False, description="是否激活")


class ToolConfig(ToolConfigBase, table=True):
    """工具配置表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="更新时间"
    )


class ToolConfigCreate(ToolConfigBase):
    """创建工具配置Schema"""
    pass


class ToolConfigUpdate(SQLModel):
    """更新工具配置Schema"""
    tool_name: Optional[str] = None
    tool_type: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: Optional[bool] = None


class ToolConfigPublic(ToolConfigBase):
    """工具配置公开Schema"""
    id: int
    created_at: datetime
    updated_at: datetime


# ==================== 会话模型 ====================

class SessionBase(SQLModel):
    """会话基础模型"""
    session_id: str = Field(max_length=100, unique=True, description="SDK会话ID")
    parent_session_id: Optional[str] = Field(default=None, max_length=100, description="父会话ID")
    session_type: str = Field(max_length=50, description="会话类型: developing/testing/review")
    status: str = Field(default="active", max_length=50, description="状态")
    checkpoint_data: Optional[dict] = Field(default=None, sa_type=JSON, description="检查点数据")


class Session(SessionBase, table=True):
    """会话表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", nullable=False, ondelete="CASCADE")
    started_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="会话开始时间"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        description="会话完成时间"
    )
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="更新时间"
    )
    
    # 关系
    project: Optional[Project] = Relationship(back_populates="sessions")


class SessionCreate(SessionBase):
    """创建会话Schema"""
    project_id: int


class SessionUpdate(SQLModel):
    """更新会话Schema"""
    session_id: Optional[str] = None
    parent_session_id: Optional[str] = None
    session_type: Optional[str] = None
    status: Optional[str] = None
    checkpoint_data: Optional[dict] = None
    completed_at: Optional[datetime] = None


class SessionPublic(SessionBase):
    """会话公开Schema"""
    id: int
    project_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ==================== 错误记录模型 ====================

class ErrorBase(SQLModel):
    """错误记录基础模型"""
    error_type: str = Field(max_length=100, description="错误类型")
    error_message: str = Field(description="错误消息")
    error_context: Optional[dict] = Field(default=None, sa_type=JSON, description="错误上下文")
    stack_trace: Optional[str] = Field(default=None, description="堆栈跟踪")
    status: str = Field(default="unresolved", max_length=50, description="状态")


class Error(ErrorBase, table=True):
    """错误记录表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", nullable=False, ondelete="CASCADE")
    resolved_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        description="解决时间"
    )
    created_at: datetime = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),
        description="创建时间"
    )
    
    # 关系
    project: Optional[Project] = Relationship(back_populates="errors")


class ErrorCreate(ErrorBase):
    """创建错误记录Schema"""
    project_id: int


class ErrorUpdate(SQLModel):
    """更新错误记录Schema"""
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    error_context: Optional[dict] = None
    stack_trace: Optional[str] = None
    status: Optional[str] = None
    resolved_at: Optional[datetime] = None


class ErrorPublic(ErrorBase):
    """错误记录公开Schema"""
    id: int
    project_id: int
    resolved_at: Optional[datetime] = None
    created_at: datetime


# ==================== 批量返回模型 ====================

class ProjectsPublic(SQLModel):
    """项目列表"""
    data: list[ProjectPublic]
    count: int


class ProcessStagesPublic(SQLModel):
    """流程阶段列表"""
    data: list[ProcessStagePublic]
    count: int


class FunctionModulesPublic(SQLModel):
    """功能模块列表"""
    data: list[FunctionModulePublic]
    count: int


class TestCasesPublic(SQLModel):
    """测试用例列表"""
    data: list[TestCasePublic]
    count: int


class ExecutionLogsPublic(SQLModel):
    """执行日志列表"""
    data: list[ExecutionLogPublic]
    count: int
    page: int
    page_size: int


class DocumentsPublic(SQLModel):
    """文档列表"""
    data: list[DocumentPublic]
    count: int


class SystemConfigsPublic(SQLModel):
    """系统配置列表"""
    data: list[SystemConfigPublic]
    count: int


class ToolConfigsPublic(SQLModel):
    """工具配置列表"""
    data: list[ToolConfigPublic]
    count: int


class SessionsPublic(SQLModel):
    """会话列表"""
    data: list[SessionPublic]
    count: int


class ErrorsPublic(SQLModel):
    """错误记录列表"""
    data: list[ErrorPublic]
    count: int
