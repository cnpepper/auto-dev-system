"""
Hook系统

在关键节点执行自定义逻辑，支持扩展和自定义业务流程
"""
from typing import Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class HookType(str, Enum):
    """Hook类型枚举"""
    # 项目相关
    PROJECT_START = "project_start"
    PROJECT_COMPLETE = "project_complete"
    PROJECT_PAUSE = "project_pause"
    PROJECT_RESUME = "project_resume"
    PROJECT_FAIL = "project_fail"
    
    # 阶段相关
    STAGE_START = "stage_start"
    STAGE_COMPLETE = "stage_complete"
    STAGE_FAIL = "stage_fail"
    STAGE_APPROVE = "stage_approve"
    STAGE_REJECT = "stage_reject"
    
    # 模块相关
    MODULE_START = "module_start"
    MODULE_COMPLETE = "module_complete"
    MODULE_FAIL = "module_fail"
    
    # 测试相关
    TEST_START = "test_start"
    TEST_COMPLETE = "test_complete"
    TEST_FAIL = "test_fail"
    
    # 文档相关
    DOCUMENT_LOADED = "document_loaded"
    DOCUMENT_VALIDATED = "document_validated"


@dataclass
class HookContext:
    """Hook上下文"""
    hook_type: HookType
    project_id: Optional[int] = None
    stage_id: Optional[int] = None
    module_id: Optional[int] = None
    data: Optional[dict] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class HookManager:
    """
    Hook管理器
    
    管理Hook的注册和执行
    """
    
    def __init__(self):
        self.hooks: dict[HookType, list[Callable]] = {
            hook_type: [] for hook_type in HookType
        }
    
    def register_hook(self, hook_type: HookType, hook_func: Callable) -> None:
        """
        注册Hook
        
        Args:
            hook_type: Hook类型
            hook_func: Hook函数，接受HookContext参数
        """
        self.hooks[hook_type].append(hook_func)
    
    def unregister_hook(self, hook_type: HookType, hook_func: Callable) -> None:
        """
        注销Hook
        
        Args:
            hook_type: Hook类型
            hook_func: Hook函数
        """
        if hook_func in self.hooks[hook_type]:
            self.hooks[hook_type].remove(hook_func)
    
    async def execute_hooks(self, hook_type: HookType, context: HookContext) -> list[Any]:
        """
        执行指定类型的所有Hook
        
        Args:
            hook_type: Hook类型
            context: Hook上下文
            
        Returns:
            所有Hook的执行结果
        """
        results = []
        
        for hook_func in self.hooks[hook_type]:
            try:
                # 执行Hook函数
                result = await hook_func(context) if asyncio.iscoroutinefunction(hook_func) else hook_func(context)
                results.append(result)
            except Exception as e:
                # 记录错误但继续执行其他Hook
                print(f"Hook {hook_func.__name__} failed: {str(e)}")
                results.append(None)
        
        return results
    
    def clear_hooks(self, hook_type: Optional[HookType] = None) -> None:
        """
        清除Hook
        
        Args:
            hook_type: 如果指定，只清除该类型的Hook；否则清除所有Hook
        """
        if hook_type:
            self.hooks[hook_type] = []
        else:
            self.hooks = {hook_type: [] for hook_type in HookType}


# 全局Hook管理器实例
hook_manager = HookManager()


# ==================== 示例Hook函数 ====================

async def notify_project_start(context: HookContext) -> None:
    """项目启动通知Hook"""
    print(f"[Hook] Project {context.project_id} started at {context.timestamp}")
    # TODO: 发送通知、记录日志等


async def validate_documents_before_start(context: HookContext) -> bool:
    """项目启动前验证文档Hook"""
    print(f"[Hook] Validating documents for project {context.project_id}")
    # TODO: 调用DocumentManager验证文档
    return True


async def log_stage_completion(context: HookContext) -> None:
    """阶段完成日志Hook"""
    print(f"[Hook] Stage {context.stage_id} completed at {context.timestamp}")
    # TODO: 记录详细日志


# 注册示例Hook
hook_manager.register_hook(HookType.PROJECT_START, notify_project_start)
hook_manager.register_hook(HookType.PROJECT_START, validate_documents_before_start)
hook_manager.register_hook(HookType.STAGE_COMPLETE, log_stage_completion)


# 需要导入asyncio
import asyncio
