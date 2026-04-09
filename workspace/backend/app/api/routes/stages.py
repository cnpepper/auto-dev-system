"""
流程阶段管理API路由
"""
from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    ProcessStage,
    ProcessStagePublic,
    ProcessStageUpdate,
    FunctionModule,
    FunctionModulePublic,
    FunctionModulesPublic,
    ExecutionLog,
    ExecutionLogPublic,
    ExecutionLogsPublic,
    TestReport,
    TestReportPublic,
)
import app.crud_ai_programming as crud

router = APIRouter()


@router.get("/{stage_id}", response_model=ProcessStagePublic)
def read_stage(
    session: SessionDep,
    current_user: CurrentUser,
    stage_id: int,
):
    """
    获取单个流程阶段详情
    """
    stage = crud.get_process_stage(session=session, stage_id=stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    return stage


@router.patch("/{stage_id}", response_model=ProcessStagePublic)
def update_stage(
    session: SessionDep,
    current_user: CurrentUser,
    stage_id: int,
    stage_in: ProcessStageUpdate,
):
    """
    更新流程阶段信息
    """
    db_stage = crud.get_process_stage(session=session, stage_id=stage_id)
    if not db_stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    stage = crud.update_process_stage(
        session=session,
        db_stage=db_stage,
        stage_in=stage_in,
    )
    return stage


@router.post("/{stage_id}/approve", response_model=ProcessStagePublic)
def approve_stage(
    session: SessionDep,
    current_user: CurrentUser,
    stage_id: int,
):
    """
    人工审批通过
    
    将阶段状态改为 approved，流程编排引擎将继续执行下一阶段
    """
    db_stage = crud.get_process_stage(session=session, stage_id=stage_id)
    if not db_stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    # 检查阶段状态
    if db_stage.status != "pending_review":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve stage with status: {db_stage.status}"
        )
    
    # 更新阶段状态
    update_data = ProcessStageUpdate(status="approved")
    stage = crud.update_process_stage(
        session=session,
        db_stage=db_stage,
        stage_in=update_data,
    )
    
    # TODO: 触发流程编排引擎继续执行
    
    return stage


@router.post("/{stage_id}/reject", response_model=ProcessStagePublic)
def reject_stage(
    session: SessionDep,
    current_user: CurrentUser,
    stage_id: int,
    reason: str = "",
):
    """
    人工审批拒绝
    
    将阶段状态改为 rejected，流程编排引擎将进行回退或终止
    """
    db_stage = crud.get_process_stage(session=session, stage_id=stage_id)
    if not db_stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    # 检查阶段状态
    if db_stage.status != "pending_review":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reject stage with status: {db_stage.status}"
        )
    
    # 更新阶段状态
    update_data = ProcessStageUpdate(status="rejected")
    stage = crud.update_process_stage(
        session=session,
        db_stage=db_stage,
        stage_in=update_data,
    )
    
    # TODO: 触发流程编排引擎回退或终止
    
    return stage


@router.get("/{stage_id}/modules", response_model=FunctionModulesPublic)
def read_stage_modules(
    session: SessionDep,
    current_user: CurrentUser,
    stage_id: int,
):
    """
    获取阶段的所有功能模块
    """
    stage = crud.get_process_stage(session=session, stage_id=stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    modules = crud.get_function_modules_by_stage(session=session, stage_id=stage_id)
    return FunctionModulesPublic(data=modules, count=len(modules))


@router.get("/{stage_id}/logs", response_model=ExecutionLogsPublic)
def read_stage_logs(
    session: SessionDep,
    current_user: CurrentUser,
    stage_id: int,
    page: int = 1,
    page_size: int = 50,
):
    """
    获取阶段的执行日志(分页)
    """
    stage = crud.get_process_stage(session=session, stage_id=stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    skip = (page - 1) * page_size
    logs = crud.get_execution_logs_by_stage(
        session=session,
        stage_id=stage_id,
        skip=skip,
        limit=page_size,
    )
    count = crud.count_execution_logs_by_stage(session=session, stage_id=stage_id)
    
    return ExecutionLogsPublic(
        data=logs,
        count=count,
        page=page,
        page_size=page_size,
    )


@router.get("/{stage_id}/reports", response_model=list[TestReportPublic])
def read_stage_reports(
    session: SessionDep,
    current_user: CurrentUser,
    stage_id: int,
):
    """
    获取阶段的所有测试报告
    """
    stage = crud.get_process_stage(session=session, stage_id=stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    
    reports = crud.get_test_reports_by_stage(session=session, stage_id=stage_id)
    return reports
