"""
会话管理模块

管理AI工具的会话状态，支持会话的创建、检查点、恢复和清理
"""
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Session

from app.models import (
    Session as SessionModel,
    SessionCreate,
    SessionUpdate,
)
import app.crud_ai_programming as crud
from app.services.codebuddy_adapter import CodeBuddyAdapter, AIToolConfig


class SessionManager:
    """
    会话管理器
    
    管理AI工具的会话状态
    """
    
    def __init__(self, session: Session, ai_adapter: Optional[CodeBuddyAdapter] = None):
        self.session = session
        self.ai_adapter = ai_adapter
    
    async def create_session(
        self,
        project_id: int,
        project_path: str,
        session_type: str,
        parent_session_id: Optional[str] = None,
    ) -> SessionModel:
        """
        创建新的AI工具会话
        
        Args:
            project_id: 项目ID
            project_path: 项目路径
            session_type: 会话类型（developing/testing/review）
            parent_session_id: 父会话ID（可选）
            
        Returns:
            创建的会话对象
        """
        # 调用AI工具适配器创建会话
        if self.ai_adapter:
            response = await self.ai_adapter.create_session(
                project_path=project_path,
                context={"project_id": project_id, "session_type": session_type},
            )
            
            if not response.success:
                raise RuntimeError(f"Failed to create AI session: {response.error_message}")
            
            sdk_session_id = response.session_id
        else:
            # 如果没有AI适配器，生成模拟会话ID
            import uuid
            sdk_session_id = f"mock_{uuid.uuid4().hex[:12]}"
        
        # 创建会话记录
        session_create = SessionCreate(
            project_id=project_id,
            session_id=sdk_session_id,
            parent_session_id=parent_session_id,
            session_type=session_type,
            status="active",
        )
        
        return crud.create_session(
            session=self.session,
            session_create=session_create,
        )
    
    async def get_or_create_session(
        self,
        project_id: int,
        project_path: str,
        session_type: str,
    ) -> SessionModel:
        """
        获取或创建会话
        
        如果项目有活跃的会话，返回该会话；否则创建新会话
        
        Args:
            project_id: 项目ID
            project_path: 项目路径
            session_type: 会话类型
            
        Returns:
            会话对象
        """
        # 查找项目的活跃会话
        sessions = crud.get_sessions_by_project(
            session=self.session,
            project_id=project_id,
        )
        
        active_sessions = [
            s for s in sessions
            if s.status == "active" and s.session_type == session_type
        ]
        
        if active_sessions:
            # 返回最新的活跃会话
            return active_sessions[0]
        
        # 创建新会话
        return await self.create_session(
            project_id=project_id,
            project_path=project_path,
            session_type=session_type,
        )
    
    async def checkpoint_session(self, session_id: int) -> SessionModel:
        """
        创建会话检查点
        
        Args:
            session_id: 会话ID（数据库ID）
            
        Returns:
            更新后的会话对象
        """
        db_session = crud.get_session(session=self.session, session_id=session_id)
        if not db_session:
            raise ValueError(f"Session {session_id} not found")
        
        # 调用AI工具适配器创建检查点
        if self.ai_adapter:
            response = await self.ai_adapter.checkpoint_session(
                session_id=db_session.session_id,
            )
            
            if not response.success:
                raise RuntimeError(f"Failed to create checkpoint: {response.error_message}")
            
            checkpoint_data = response.result
        else:
            # 模拟检查点数据
            checkpoint_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "files_modified": 0,
            }
        
        # 更新会话记录
        update_data = SessionUpdate(checkpoint_data=checkpoint_data)
        
        return crud.update_session(
            session=self.session,
            db_session=db_session,
            session_in=update_data,
        )
    
    async def restore_session(self, session_id: int) -> SessionModel:
        """
        从检查点恢复会话
        
        Args:
            session_id: 会话ID（数据库ID）
            
        Returns:
            更新后的会话对象
        """
        db_session = crud.get_session(session=self.session, session_id=session_id)
        if not db_session:
            raise ValueError(f"Session {session_id} not found")
        
        if not db_session.checkpoint_data:
            raise ValueError(f"No checkpoint found for session {session_id}")
        
        # 调用AI工具适配器恢复会话
        if self.ai_adapter:
            response = await self.ai_adapter.restore_session(
                session_id=db_session.session_id,
                checkpoint_data=db_session.checkpoint_data,
            )
            
            if not response.success:
                raise RuntimeError(f"Failed to restore session: {response.error_message}")
        
        # 更新会话状态为活跃
        update_data = SessionUpdate(status="active")
        
        return crud.update_session(
            session=self.session,
            db_session=db_session,
            session_in=update_data,
        )
    
    async def close_session(self, session_id: int) -> SessionModel:
        """
        关闭会话
        
        Args:
            session_id: 会话ID（数据库ID）
            
        Returns:
            更新后的会话对象
        """
        db_session = crud.get_session(session=self.session, session_id=session_id)
        if not db_session:
            raise ValueError(f"Session {session_id} not found")
        
        # 调用AI工具适配器关闭会话
        if self.ai_adapter:
            response = await self.ai_adapter.close_session(
                session_id=db_session.session_id,
            )
            
            if not response.success:
                # 记录错误但继续关闭本地会话
                print(f"Warning: Failed to close AI session: {response.error_message}")
        
        # 更新会话状态
        update_data = SessionUpdate(
            status="closed",
            completed_at=datetime.now(timezone.utc),
        )
        
        return crud.update_session(
            session=self.session,
            db_session=db_session,
            session_in=update_data,
        )
    
    async def pause_session(self, session_id: int) -> SessionModel:
        """
        暂停会话
        
        Args:
            session_id: 会话ID（数据库ID）
            
        Returns:
            更新后的会话对象
        """
        db_session = crud.get_session(session=self.session, session_id=session_id)
        if not db_session:
            raise ValueError(f"Session {session_id} not found")
        
        # 创建检查点
        if self.ai_adapter and not db_session.checkpoint_data:
            await self.checkpoint_session(session_id=session_id)
            db_session = crud.get_session(session=self.session, session_id=session_id)
        
        # 更新会话状态
        update_data = SessionUpdate(status="paused")
        
        return crud.update_session(
            session=self.session,
            db_session=db_session,
            session_in=update_data,
        )
    
    async def resume_session(self, session_id: int) -> SessionModel:
        """
        恢复暂停的会话
        
        Args:
            session_id: 会话ID（数据库ID）
            
        Returns:
            更新后的会话对象
        """
        db_session = crud.get_session(session=self.session, session_id=session_id)
        if not db_session:
            raise ValueError(f"Session {session_id} not found")
        
        # 如果有检查点，从检查点恢复
        if db_session.checkpoint_data and self.ai_adapter:
            await self.restore_session(session_id=session_id)
        else:
            # 直接更新状态
            update_data = SessionUpdate(status="active")
            db_session = crud.update_session(
                session=self.session,
                db_session=db_session,
                session_in=update_data,
            )
        
        return db_session
    
    def get_active_session(self, project_id: int) -> Optional[SessionModel]:
        """
        获取项目的活跃会话
        
        Args:
            project_id: 项目ID
            
        Returns:
            活跃的会话对象，如果没有则返回None
        """
        sessions = crud.get_sessions_by_project(
            session=self.session,
            project_id=project_id,
        )
        
        active_sessions = [s for s in sessions if s.status == "active"]
        
        return active_sessions[0] if active_sessions else None
