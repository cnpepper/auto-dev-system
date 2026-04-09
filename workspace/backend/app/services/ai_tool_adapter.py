"""
AI工具适配器基类

定义AI工具的标准接口，支持不同AI编程工具的统一调用
"""
from abc import ABC, abstractmethod
from typing import Optional, Any
from pydantic import BaseModel


class AIToolConfig(BaseModel):
    """AI工具配置"""
    tool_name: str
    tool_type: str
    config: dict


class AIToolResponse(BaseModel):
    """AI工具响应"""
    success: bool
    session_id: Optional[str] = None
    result: Optional[Any] = None
    error_message: Optional[str] = None


class BaseAIToolAdapter(ABC):
    """
    AI工具适配器基类
    
    定义AI工具的标准接口，所有AI工具适配器都必须实现这些方法
    """
    
    def __init__(self, config: AIToolConfig):
        self.config = config
    
    @abstractmethod
    async def create_session(self, project_path: str, context: dict) -> AIToolResponse:
        """
        创建AI工具会话
        
        Args:
            project_path: 项目路径
            context: 上下文信息（包括文档、需求等）
            
        Returns:
            AIToolResponse: 包含会话ID的响应
        """
        pass
    
    @abstractmethod
    async def send_instruction(
        self,
        session_id: str,
        instruction: str,
        context: Optional[dict] = None,
    ) -> AIToolResponse:
        """
        发送指令给AI工具
        
        Args:
            session_id: 会话ID
            instruction: 指令内容
            context: 额外的上下文信息
            
        Returns:
            AIToolResponse: 执行结果
        """
        pass
    
    @abstractmethod
    async def get_session_status(self, session_id: str) -> AIToolResponse:
        """
        获取会话状态
        
        Args:
            session_id: 会话ID
            
        Returns:
            AIToolResponse: 会话状态信息
        """
        pass
    
    @abstractmethod
    async def close_session(self, session_id: str) -> AIToolResponse:
        """
        关闭会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            AIToolResponse: 关闭结果
        """
        pass
    
    @abstractmethod
    async def execute_test(self, session_id: str, test_command: str) -> AIToolResponse:
        """
        执行测试
        
        Args:
            session_id: 会话ID
            test_command: 测试命令
            
        Returns:
            AIToolResponse: 测试结果
        """
        pass
    
    @abstractmethod
    async def checkpoint_session(self, session_id: str) -> AIToolResponse:
        """
        创建会话检查点
        
        Args:
            session_id: 会话ID
            
        Returns:
            AIToolResponse: 检查点数据
        """
        pass
    
    @abstractmethod
    async def restore_session(self, session_id: str, checkpoint_data: dict) -> AIToolResponse:
        """
        从检查点恢复会话
        
        Args:
            session_id: 会话ID
            checkpoint_data: 检查点数据
            
        Returns:
            AIToolResponse: 恢复结果
        """
        pass
