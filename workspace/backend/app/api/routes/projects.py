"""
项目管理API路由
"""
from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectPublic,
    ProjectsPublic,
    ProcessStage,
    ProcessStagePublic,
    ProcessStagesPublic,
)
from app.services.process_engine import ProcessEngine
import app.crud_ai_programming as crud

router = APIRouter()



@router.get("/", response_model=ProjectsPublic)
def read_projects(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
):
    """
    获取项目列表
    """
    projects = crud.get_projects(session=session, skip=skip, limit=limit)
    count = crud.count_projects(session=session)
    return ProjectsPublic(data=projects, count=count)


@router.get("/{project_id}", response_model=ProjectPublic)
def read_project(
    session: SessionDep,
    current_user: CurrentUser,
    project_id: int,
):
    """
    获取单个项目详情
    """
    project = crud.get_project(session=session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=ProjectPublic, status_code=201)
def create_project(
    session: SessionDep,
    current_user: CurrentUser,
    project_in: ProjectCreate,
):
    """
    创建新项目
    """
    project = crud.create_project(session=session, project_create=project_in)
    return project


@router.patch("/{project_id}", response_model=ProjectPublic)
def update_project(
    session: SessionDep,
    current_user: CurrentUser,
    project_id: int,
    project_in: ProjectUpdate,
):
    """
    更新项目信息
    """
    db_project = crud.get_project(session=session, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = crud.update_project(
        session=session,
        db_project=db_project,
        project_in=project_in,
    )
    return project


@router.delete("/{project_id}")
def delete_project(
    session: SessionDep,
    current_user: CurrentUser,
    project_id: int,
):
    """
    删除项目
    """
    project = crud.get_project(session=session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    success = crud.delete_project(session=session, project_id=project_id)
    return {"message": "Project deleted successfully" if success else "Failed to delete project"}


@router.post("/{project_id}/start", response_model=ProjectPublic)
def start_project(
    session: SessionDep,
    current_user: CurrentUser,
    project_id: int,
):
    """
    启动项目流程
    
    将项目状态从 idle 改为 running，并创建初始流程阶段
    """
    db_project = crud.get_project(session=session, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 检查项目状态
    if db_project.status not in ["idle", "paused"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start project with status: {db_project.status}"
        )
    
    # 调用流程引擎：更新状态 + 创建阶段 + 写日志
    engine = ProcessEngine(session=session)
    try:
        project = engine.start_project(project_id=project_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return project



@router.post("/{project_id}/pause", response_model=ProjectPublic)
def pause_project(
    session: SessionDep,
    current_user: CurrentUser,
    project_id: int,
):
    """
    暂停项目
    
    将项目状态改为 paused
    """
    db_project = crud.get_project(session=session, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 检查项目状态
    if db_project.status != "running":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot pause project with status: {db_project.status}"
        )
    
    # 调用流程引擎暂停
    engine = ProcessEngine(session=session)
    try:
        project = engine.pause_project(project_id=project_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return project



@router.post("/{project_id}/resume", response_model=ProjectPublic)
def resume_project(
    session: SessionDep,
    current_user: CurrentUser,
    project_id: int,
):
    """
    恢复项目
    
    将项目状态从 paused 改为 running
    """
    db_project = crud.get_project(session=session, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 检查项目状态
    if db_project.status != "paused":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot resume project with status: {db_project.status}"
        )
    
    # 调用流程引擎恢复
    engine = ProcessEngine(session=session)
    try:
        project = engine.resume_project(project_id=project_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return project



@router.get("/{project_id}/stages", response_model=ProcessStagesPublic)
def read_project_stages(
    session: SessionDep,
    current_user: CurrentUser,
    project_id: int,
):
    """
    获取项目的所有流程阶段
    """
    project = crud.get_project(session=session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    stages = crud.get_process_stages_by_project(session=session, project_id=project_id)
    return ProcessStagesPublic(data=stages, count=len(stages))
