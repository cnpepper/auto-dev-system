"""
配置管理API路由
"""
from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    SystemConfig,
    SystemConfigCreate,
    SystemConfigUpdate,
    SystemConfigPublic,
    SystemConfigsPublic,
    ToolConfig,
    ToolConfigCreate,
    ToolConfigUpdate,
    ToolConfigPublic,
    ToolConfigsPublic,
)
import app.crud_ai_programming as crud

router = APIRouter()


# ==================== 系统配置API ====================

@router.get("/system", response_model=SystemConfigsPublic)
def read_system_configs(
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    获取所有系统配置
    """
    configs = crud.get_system_configs(session=session)
    return SystemConfigsPublic(data=configs, count=len(configs))


@router.get("/system/{config_key}", response_model=SystemConfigPublic)
def read_system_config(
    session: SessionDep,
    current_user: CurrentUser,
    config_key: str,
):
    """
    根据key获取系统配置
    """
    config = crud.get_system_config_by_key(session=session, config_key=config_key)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return config


@router.post("/system", response_model=SystemConfigPublic, status_code=201)
def create_system_config(
    session: SessionDep,
    current_user: CurrentUser,
    config_in: SystemConfigCreate,
):
    """
    创建系统配置
    """
    # 检查key是否已存在
    existing = crud.get_system_config_by_key(session=session, config_key=config_in.config_key)
    if existing:
        raise HTTPException(status_code=400, detail="Config key already exists")
    
    config = crud.create_system_config(session=session, config_create=config_in)
    return config


@router.patch("/system/{config_id}", response_model=SystemConfigPublic)
def update_system_config(
    session: SessionDep,
    current_user: CurrentUser,
    config_id: int,
    config_in: SystemConfigUpdate,
):
    """
    更新系统配置
    """
    db_config = crud.get_system_config(session=session, config_id=config_id)
    if not db_config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    config = crud.update_system_config(
        session=session,
        db_config=db_config,
        config_in=config_in,
    )
    return config


# ==================== 工具配置API ====================

@router.get("/tools", response_model=ToolConfigsPublic)
def read_tool_configs(
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    获取所有工具配置
    """
    configs = crud.get_tool_configs(session=session)
    return ToolConfigsPublic(data=configs, count=len(configs))


@router.get("/tools/{tool_id}", response_model=ToolConfigPublic)
def read_tool_config(
    session: SessionDep,
    current_user: CurrentUser,
    tool_id: int,
):
    """
    获取单个工具配置
    """
    config = crud.get_tool_config(session=session, tool_id=tool_id)
    if not config:
        raise HTTPException(status_code=404, detail="Tool config not found")
    return config


@router.post("/tools", response_model=ToolConfigPublic, status_code=201)
def create_tool_config(
    session: SessionDep,
    current_user: CurrentUser,
    tool_in: ToolConfigCreate,
):
    """
    创建工具配置
    """
    config = crud.create_tool_config(session=session, tool_create=tool_in)
    return config


@router.patch("/tools/{tool_id}", response_model=ToolConfigPublic)
def update_tool_config(
    session: SessionDep,
    current_user: CurrentUser,
    tool_id: int,
    tool_in: ToolConfigUpdate,
):
    """
    更新工具配置
    """
    db_tool = crud.get_tool_config(session=session, tool_id=tool_id)
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool config not found")
    
    tool = crud.update_tool_config(
        session=session,
        db_tool=db_tool,
        tool_in=tool_in,
    )
    return tool


@router.post("/tools/{tool_id}/activate", response_model=ToolConfigPublic)
def activate_tool(
    session: SessionDep,
    current_user: CurrentUser,
    tool_id: int,
):
    """
    激活工具
    """
    db_tool = crud.get_tool_config(session=session, tool_id=tool_id)
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool config not found")
    
    update_data = ToolConfigUpdate(is_active=True)
    tool = crud.update_tool_config(
        session=session,
        db_tool=db_tool,
        tool_in=update_data,
    )
    return tool


@router.post("/tools/{tool_id}/deactivate", response_model=ToolConfigPublic)
def deactivate_tool(
    session: SessionDep,
    current_user: CurrentUser,
    tool_id: int,
):
    """
    停用工具
    """
    db_tool = crud.get_tool_config(session=session, tool_id=tool_id)
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool config not found")
    
    update_data = ToolConfigUpdate(is_active=False)
    tool = crud.update_tool_config(
        session=session,
        db_tool=db_tool,
        tool_in=update_data,
    )
    return tool
