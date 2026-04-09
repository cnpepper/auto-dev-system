"""
文档管理模块

负责扫描、识别和加载项目文档
"""
import os
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

from sqlmodel import Session

from app.models import (
    Document,
    DocumentCreate,
)
import app.crud_ai_programming as crud


class DocumentType:
    """文档类型枚举"""
    PRD = "prd"
    DESIGN = "design"
    PROTOTYPE = "prototype"
    TEST_REPORT = "test_report"


class DocumentManager:
    """
    文档管理器
    
    负责扫描、识别和加载项目文档
    """
    
    # 文档类型识别规则
    DOCUMENT_PATTERNS = {
        DocumentType.PRD: [
            "产品需求文档",
            "PRD",
            "需求文档",
            "requirements",
        ],
        DocumentType.DESIGN: [
            "技术设计文档",
            "技术方案",
            "数据库设计",
            "接口设计",
            "design",
            "architecture",
        ],
        DocumentType.PROTOTYPE: [
            "原型",
            "prototype",
            "mock",
        ],
        DocumentType.TEST_REPORT: [
            "测试报告",
            "test_report",
            "测试结果",
        ],
    }
    
    def __init__(self, session: Session):
        self.session = session
    
    def scan_documents(self, project_id: int, document_dir: str) -> list[Document]:
        """
        扫描文档目录，识别并加载文档
        
        Args:
            project_id: 项目ID
            document_dir: 文档目录路径
            
        Returns:
            识别到的文档列表
        """
        doc_path = Path(document_dir)
        
        if not doc_path.exists():
            raise ValueError(f"Document directory not found: {document_dir}")
        
        if not doc_path.is_dir():
            raise ValueError(f"Path is not a directory: {document_dir}")
        
        documents = []
        
        # 扫描目录下的所有文件
        for file_path in doc_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".md", ".txt", ".pdf", ".docx"]:
                # 识别文档类型
                doc_type = self._identify_document_type(file_path)
                
                # 创建文档记录
                doc_create = DocumentCreate(
                    project_id=project_id,
                    doc_type=doc_type,
                    file_path=str(file_path.absolute()),
                    file_name=file_path.name,
                    status="pending",
                )
                
                doc = crud.create_document(
                    session=self.session,
                    doc_create=doc_create,
                )
                documents.append(doc)
        
        return documents
    
    def _identify_document_type(self, file_path: Path) -> str:
        """
        识别文档类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            文档类型
        """
        file_name = file_path.name.lower()
        file_stem = file_path.stem.lower()
        
        # 检查文件名是否匹配某种文档类型
        for doc_type, patterns in self.DOCUMENT_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in file_name or pattern.lower() in file_stem:
                    return doc_type
        
        # 默认返回 design 类型
        return DocumentType.DESIGN
    
    def load_document_content(self, document_id: int) -> str:
        """
        加载文档内容
        
        Args:
            document_id: 文档ID
            
        Returns:
            文档内容
        """
        document = crud.get_document(session=self.session, document_id=document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        file_path = Path(document.file_path)
        
        if not file_path.exists():
            raise ValueError(f"Document file not found: {file_path}")
        
        # 读取文档内容
        if file_path.suffix == ".md" or file_path.suffix == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        elif file_path.suffix == ".pdf":
            # TODO: 使用PDF解析库读取PDF内容
            content = "[PDF content - parsing not implemented]"
        elif file_path.suffix == ".docx":
            # TODO: 使用docx库读取Word文档内容
            content = "[DOCX content - parsing not implemented]"
        else:
            content = f"[Unsupported file format: {file_path.suffix}]"
        
        # 更新文档状态为已加载
        from app.models import DocumentUpdate
        update_data = DocumentUpdate(status="loaded")
        crud.update_document(
            session=self.session,
            db_doc=document,
            doc_in=update_data,
        )
        
        return content
    
    def get_documents_by_type(
        self,
        project_id: int,
        doc_type: str,
    ) -> list[Document]:
        """
        获取指定类型的文档
        
        Args:
            project_id: 项目ID
            doc_type: 文档类型
            
        Returns:
            文档列表
        """
        all_docs = crud.get_documents_by_project(
            session=self.session,
            project_id=project_id,
        )
        
        return [doc for doc in all_docs if doc.doc_type == doc_type]
    
    def validate_documents(self, project_id: int) -> dict:
        """
        验证项目文档是否完整
        
        检查项目是否包含必要的文档：
        - PRD文档
        - 技术设计文档
        
        Args:
            project_id: 项目ID
            
        Returns:
            验证结果，包含缺失的文档类型
        """
        documents = crud.get_documents_by_project(
            session=self.session,
            project_id=project_id,
        )
        
        doc_types = {doc.doc_type for doc in documents}
        
        required_types = {
            DocumentType.PRD,
            DocumentType.DESIGN,
        }
        
        missing_types = required_types - doc_types
        
        return {
            "is_valid": len(missing_types) == 0,
            "missing_types": list(missing_types),
            "existing_types": list(doc_types),
        }
    
    def summarize_documents(self, project_id: int) -> dict:
        """
        汇总项目文档信息
        
        Args:
            project_id: 项目ID
            
        Returns:
            文档汇总信息
        """
        documents = crud.get_documents_by_project(
            session=self.session,
            project_id=project_id,
        )
        
        summary = {
            "total_count": len(documents),
            "by_type": {},
            "by_status": {},
        }
        
        for doc in documents:
            # 按类型统计
            if doc.doc_type not in summary["by_type"]:
                summary["by_type"][doc.doc_type] = 0
            summary["by_type"][doc.doc_type] += 1
            
            # 按状态统计
            if doc.status not in summary["by_status"]:
                summary["by_status"][doc.status] = 0
            summary["by_status"][doc.status] += 1
        
        return summary


# 需要在 crud_ai_programming.py 中添加 get_document 函数
def get_document(*, session: Session, document_id: int) -> Document | None:
    """获取单个文档"""
    return session.get(Document, document_id)


# 添加到 crud_ai_programming.py
import app.crud_ai_programming as crud_module
if not hasattr(crud_module, 'get_document'):
    setattr(crud_module, 'get_document', get_document)
