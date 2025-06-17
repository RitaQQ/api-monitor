from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import uuid

class TestStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"
    NOT_TESTED = "not_tested"

class ProjectStatus(Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

@dataclass
class ProductTag:
    """產品標籤"""
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductTag':
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        )

@dataclass
class TestCase:
    """測試案例 (User Story 格式)"""
    id: str
    title: str
    user_role: str  # 使用者角色
    feature_description: str  # 功能描述
    acceptance_criteria: List[str]  # 驗收條件
    test_notes: Optional[str] = None  # 測試備註
    product_tags: List[str] = field(default_factory=list)  # 產品標籤ID列表
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'user_role': self.user_role,
            'feature_description': self.feature_description,
            'acceptance_criteria': self.acceptance_criteria,
            'test_notes': self.test_notes,
            'product_tags': self.product_tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestCase':
        return cls(
            id=data['id'],
            title=data['title'],
            user_role=data['user_role'],
            feature_description=data['feature_description'],
            acceptance_criteria=data.get('acceptance_criteria', []),
            test_notes=data.get('test_notes'),
            product_tags=data.get('product_tags', []),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        )

@dataclass
class TestResult:
    """測試結果"""
    test_case_id: str
    status: TestStatus
    notes: Optional[str] = None
    known_issues: Optional[str] = None
    blocked_reason: Optional[str] = None
    tested_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'test_case_id': self.test_case_id,
            'status': self.status.value,
            'notes': self.notes,
            'known_issues': self.known_issues,
            'blocked_reason': self.blocked_reason,
            'tested_at': self.tested_at.isoformat() if self.tested_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestResult':
        return cls(
            test_case_id=data['test_case_id'],
            status=TestStatus(data['status']),
            notes=data.get('notes'),
            known_issues=data.get('known_issues'),
            blocked_reason=data.get('blocked_reason'),
            tested_at=datetime.fromisoformat(data['tested_at']) if data.get('tested_at') else datetime.now()
        )

@dataclass
class TestProject:
    """測試專案"""
    id: str
    name: str
    test_date: datetime
    responsible_user: str  # 負責人用戶名
    selected_test_cases: List[str]  # 選擇的測試案例ID列表
    test_results: Dict[str, TestResult] = field(default_factory=dict)  # test_case_id -> TestResult
    status: ProjectStatus = ProjectStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'responsible_user': self.responsible_user,
            'selected_test_cases': self.selected_test_cases,
            'test_results': {k: v.to_dict() for k, v in self.test_results.items()},
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestProject':
        return cls(
            id=data['id'],
            name=data['name'],
            test_date=datetime.fromisoformat(data['test_date']) if data.get('test_date') else datetime.now(),
            responsible_user=data['responsible_user'],
            selected_test_cases=data.get('selected_test_cases', []),
            test_results={k: TestResult.from_dict(v) for k, v in data.get('test_results', {}).items()},
            status=ProjectStatus(data.get('status', 'draft')),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        )

@dataclass
class TestStatistics:
    """測試統計"""
    total_cases: int
    passed_cases: int
    failed_cases: int
    blocked_cases: int
    not_tested_cases: int
    pass_rate: float
    fail_rate: float
    product_stats: Dict[str, Dict[str, Any]]  # product_tag -> {'passed': int, 'failed': int, 'blocked': int, 'total': int, 'pass_rate': float}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_cases': self.total_cases,
            'passed_cases': self.passed_cases,
            'failed_cases': self.failed_cases,
            'blocked_cases': self.blocked_cases,
            'not_tested_cases': self.not_tested_cases,
            'pass_rate': self.pass_rate,
            'fail_rate': self.fail_rate,
            'product_stats': self.product_stats
        }

def generate_id() -> str:
    """生成唯一ID"""
    return str(uuid.uuid4())