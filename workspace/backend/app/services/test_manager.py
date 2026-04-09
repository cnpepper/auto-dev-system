"""
测试管理模块

负责pytest集成、测试执行和报告生成
"""
import subprocess
import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

from sqlmodel import Session

from app.models import (
    TestReport,
    TestReportCreate,
    TestCase,
    TestCaseCreate,
    ExecutionLog,
    ExecutionLogCreate,
)
import app.crud_ai_programming as crud


class TestManager:
    """
    测试管理器
    
    负责pytest集成、测试执行和报告生成
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def run_tests(
        self,
        project_id: int,
        stage_id: int,
        test_path: str,
        test_command: Optional[str] = None,
    ) -> TestReport:
        """
        执行测试
        
        Args:
            project_id: 项目ID
            stage_id: 阶段ID
            test_path: 测试文件路径
            test_command: 自定义测试命令（可选）
            
        Returns:
            测试报告
        """
        # 默认使用pytest命令
        if not test_command:
            test_command = f"pytest {test_path} -v --tb=short"
        
        # 记录日志
        self._log_info(
            stage_id=stage_id,
            message=f"开始执行测试: {test_command}",
            extra_data={"test_path": test_path},
        )
        
        try:
            # 执行测试命令
            result = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=600,  # 10分钟超时
                cwd=test_path if Path(test_path).is_dir() else str(Path(test_path).parent),
            )
            
            # 解析测试结果
            test_results = self._parse_pytest_output(result.stdout)
            
            # 生成报告文件
            report_file_path = self._generate_report_file(
                project_id=project_id,
                stage_id=stage_id,
                test_results=test_results,
                output=result.stdout,
            )
            
            # 创建测试报告记录
            report_create = TestReportCreate(
                stage_id=stage_id,
                report_file_path=report_file_path,
                total_cases=test_results["total"],
                passed_cases=test_results["passed"],
                failed_cases=test_results["failed"],
                status="completed",
            )
            
            report = crud.create_test_report(
                session=self.session,
                report_create=report_create,
            )
            
            # 记录日志
            self._log_info(
                stage_id=stage_id,
                message=f"测试执行完成: 通过 {test_results['passed']}/{test_results['total']}",
                extra_data={"report_id": report.id},
            )
            
            return report
            
        except subprocess.TimeoutExpired:
            # 超时错误
            self._log_error(
                stage_id=stage_id,
                message="测试执行超时",
                extra_data={"test_command": test_command},
            )
            
            # 创建失败报告
            report_create = TestReportCreate(
                stage_id=stage_id,
                report_file_path="",
                total_cases=0,
                passed_cases=0,
                failed_cases=0,
                status="timeout",
            )
            
            return crud.create_test_report(
                session=self.session,
                report_create=report_create,
            )
            
        except Exception as e:
            # 其他错误
            self._log_error(
                stage_id=stage_id,
                message=f"测试执行失败: {str(e)}",
                extra_data={"test_command": test_command, "error": str(e)},
            )
            
            # 创建失败报告
            report_create = TestReportCreate(
                stage_id=stage_id,
                report_file_path="",
                total_cases=0,
                passed_cases=0,
                failed_cases=0,
                status="failed",
            )
            
            return crud.create_test_report(
                session=self.session,
                report_create=report_create,
            )
    
    def _parse_pytest_output(self, output: str) -> dict:
        """
        解析pytest输出结果
        
        Args:
            output: pytest命令输出
            
        Returns:
            解析后的测试结果
        """
        # 简化的解析逻辑
        # 实际应该使用更健壮的解析方式
        lines = output.split("\n")
        
        total = 0
        passed = 0
        failed = 0
        
        for line in lines:
            if "passed" in line.lower():
                # 尝试解析 "5 passed" 这样的格式
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.lower() == "passed":
                        try:
                            passed = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass
                    elif part.lower() == "failed":
                        try:
                            failed = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass
        
        total = passed + failed
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "output": output,
        }
    
    def _generate_report_file(
        self,
        project_id: int,
        stage_id: int,
        test_results: dict,
        output: str,
    ) -> str:
        """
        生成测试报告文件
        
        Args:
            project_id: 项目ID
            stage_id: 阶段ID
            test_results: 测试结果
            output: 测试输出
            
        Returns:
            报告文件路径
        """
        # 创建报告目录
        report_dir = Path(f"reports/project_{project_id}/stage_{stage_id}")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"test_report_{timestamp}.md"
        
        # 生成Markdown报告
        report_content = f"""# 测试报告

## 基本信息

- **项目ID**: {project_id}
- **阶段ID**: {stage_id}
- **执行时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 测试结果

- **总用例数**: {test_results['total']}
- **通过数**: {test_results['passed']}
- **失败数**: {test_results['failed']}
- **通过率**: {(test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0:.2f}%

## 测试输出

```
{output}
```
"""
        
        # 写入文件
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        return str(report_file.absolute())
    
    def create_test_case(
        self,
        module_id: int,
        test_name: str,
        test_type: str,
    ) -> TestCase:
        """
        创建测试用例记录
        
        Args:
            module_id: 功能模块ID
            test_name: 测试用例名称
            test_type: 测试类型（positive/negative/exception）
            
        Returns:
            创建的测试用例
        """
        test_create = TestCaseCreate(
            module_id=module_id,
            test_name=test_name,
            test_type=test_type,
            status="pending",
        )
        
        return crud.create_test_case(
            session=self.session,
            test_create=test_create,
        )
    
    def update_test_case_status(
        self,
        test_case_id: int,
        status: str,
        error_message: Optional[str] = None,
    ) -> TestCase:
        """
        更新测试用例状态
        
        Args:
            test_case_id: 测试用例ID
            status: 新状态
            error_message: 错误消息（如果失败）
            
        Returns:
            更新后的测试用例
        """
        from app.models import TestCaseUpdate
        
        update_data = TestCaseUpdate(
            status=status,
            error_message=error_message,
            completed_at=datetime.now(timezone.utc) if status in ["passed", "failed"] else None,
        )
        
        test_case = crud.get_test_case(session=self.session, test_case_id=test_case_id)
        if not test_case:
            raise ValueError(f"Test case {test_case_id} not found")
        
        return crud.update_test_case(
            session=self.session,
            db_test=test_case,
            test_in=update_data,
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


# 需要在 crud_ai_programming.py 中添加函数
def get_test_case(*, session: Session, test_case_id: int) -> TestCase | None:
    """获取单个测试用例"""
    return session.get(TestCase, test_case_id)


# 添加到 crud_ai_programming.py
import app.crud_ai_programming as crud_module
if not hasattr(crud_module, 'get_test_case'):
    setattr(crud_module, 'get_test_case', get_test_case)
