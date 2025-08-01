"""
HR Dashboard Implementation Task Manager
OK금융그룹 HR 인력현황 대시보드 구현 작업 관리자
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import os
import subprocess

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """작업 상태"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskType(Enum):
    """작업 유형"""
    ANALYSIS = "analysis"
    DATABASE = "database"
    BACKEND = "backend"
    FRONTEND = "frontend"
    INTEGRATION = "integration"
    TESTING = "testing"


class Task:
    """개별 작업 클래스"""
    
    def __init__(self, 
                 task_id: str,
                 name: str,
                 description: str,
                 task_type: TaskType,
                 dependencies: List[str] = None,
                 command: str = None,
                 files_to_create: List[str] = None):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.task_type = task_type
        self.dependencies = dependencies or []
        self.command = command
        self.files_to_create = files_to_create or []
        self.status = TaskStatus.PENDING
        self.progress = 0
        self.start_time = None
        self.end_time = None
        self.result = None
        self.error = None
    
    def to_dict(self) -> Dict[str, Any]:
        """작업을 딕셔너리로 변환"""
        return {
            'task_id': self.task_id,
            'name': self.name,
            'description': self.description,
            'task_type': self.task_type.value,
            'status': self.status.value,
            'progress': self.progress,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'dependencies': self.dependencies,
            'result': self.result,
            'error': self.error
        }


class HRDashboardTaskManager:
    """HR 대시보드 구현 작업 관리자"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.is_running = False
        self._create_tasks()
    
    def _create_tasks(self):
        """HR 대시보드 구현 작업 목록 생성"""
        tasks_data = [
            # Phase 1: 분석 및 계획
            {
                'task_id': 'analysis_1',
                'name': '기존 구조 분석',
                'description': '현재 EHR 시스템 구조 및 데이터베이스 스키마 분석',
                'task_type': TaskType.ANALYSIS,
            },
            
            # Phase 2: 데이터베이스
            {
                'task_id': 'db_1',
                'name': 'HR 데이터베이스 모델 생성',
                'description': 'hr_employees, hr_monthly_snapshots, hr_contractors 모델 생성',
                'task_type': TaskType.DATABASE,
                'dependencies': ['analysis_1'],
                'files_to_create': ['employees/models_hr.py']
            },
            {
                'task_id': 'db_2',
                'name': '데이터베이스 마이그레이션',
                'description': 'HR 테이블 마이그레이션 실행',
                'task_type': TaskType.DATABASE,
                'dependencies': ['db_1'],
                'command': 'python manage.py makemigrations employees && python manage.py migrate'
            },
            
            # Phase 3: 백엔드 구현
            {
                'task_id': 'backend_1',
                'name': '엑셀 파서 구현',
                'description': 'HRExcelAutoParser 클래스 구현 - 자동 분류 및 파싱',
                'task_type': TaskType.BACKEND,
                'dependencies': ['db_2'],
                'files_to_create': ['employees/services/excel_parser.py']
            },
            {
                'task_id': 'backend_2',
                'name': 'HR API 뷰 구현',
                'description': 'HR 대시보드 API 엔드포인트 구현',
                'task_type': TaskType.BACKEND,
                'dependencies': ['backend_1'],
                'files_to_create': ['employees/api_views_hr.py']
            },
            {
                'task_id': 'backend_3',
                'name': 'HR URL 라우팅 설정',
                'description': 'HR API URL 패턴 추가',
                'task_type': TaskType.BACKEND,
                'dependencies': ['backend_2'],
                'files_to_create': ['employees/urls_hr.py']
            },
            
            # Phase 4: 프론트엔드 구현
            {
                'task_id': 'frontend_1',
                'name': 'HR 대시보드 메인 템플릿',
                'description': 'HR 인력현황 대시보드 메인 페이지 구현',
                'task_type': TaskType.FRONTEND,
                'dependencies': ['backend_3'],
                'files_to_create': ['templates/hr/dashboard.html']
            },
            {
                'task_id': 'frontend_2',
                'name': '국내 인력 테이블 컴포넌트',
                'description': '국내 인력현황 테이블 및 필터 구현',
                'task_type': TaskType.FRONTEND,
                'dependencies': ['frontend_1'],
                'files_to_create': ['templates/hr/domestic_table.html']
            },
            {
                'task_id': 'frontend_3',
                'name': '해외 인력 테이블 컴포넌트',
                'description': '해외 인력현황 테이블 구현',
                'task_type': TaskType.FRONTEND,
                'dependencies': ['frontend_1'],
                'files_to_create': ['templates/hr/overseas_table.html']
            },
            {
                'task_id': 'frontend_4',
                'name': '외주 현황 테이블 컴포넌트',
                'description': '외주 인력현황 테이블 및 비용 계산',
                'task_type': TaskType.FRONTEND,
                'dependencies': ['frontend_1'],
                'files_to_create': ['templates/hr/contractor_table.html']
            },
            {
                'task_id': 'frontend_5',
                'name': '시각화 차트 구현',
                'description': 'Chart.js를 활용한 인력현황 시각화',
                'task_type': TaskType.FRONTEND,
                'dependencies': ['frontend_1'],
                'files_to_create': ['static/js/hr_charts.js']
            },
            
            # Phase 5: 통합 및 테스트
            {
                'task_id': 'integration_1',
                'name': '파일 업로드 기능 구현',
                'description': '엑셀 파일 업로드 및 자동 분류 처리',
                'task_type': TaskType.INTEGRATION,
                'dependencies': ['frontend_5'],
                'files_to_create': ['static/js/hr_upload.js']
            },
            {
                'task_id': 'integration_2',
                'name': '메뉴 및 네비게이션 추가',
                'description': 'HR 대시보드 메뉴 항목 추가',
                'task_type': TaskType.INTEGRATION,
                'dependencies': ['integration_1'],
            },
            {
                'task_id': 'testing_1',
                'name': '기능 테스트',
                'description': '파일 업로드, 데이터 파싱, 시각화 테스트',
                'task_type': TaskType.TESTING,
                'dependencies': ['integration_2'],
            },
        ]
        
        # Task 객체 생성
        for task_data in tasks_data:
            task = Task(**task_data)
            self.tasks[task.task_id] = task
    
    def print_progress(self, task: Task):
        """진행상황 출력"""
        print(f"\n{'='*60}")
        print(f"작업: {task.name}")
        print(f"상태: {task.status.value}")
        print(f"진행률: {task.progress}%")
        print(f"설명: {task.description}")
        if task.error:
            print(f"오류: {task.error}")
        print(f"{'='*60}\n")
    
    def calculate_overall_progress(self) -> float:
        """전체 진행률 계산"""
        if not self.tasks:
            return 0.0
        
        completed_tasks = sum(1 for task in self.tasks.values() 
                            if task.status == TaskStatus.COMPLETED)
        return (completed_tasks / len(self.tasks)) * 100
    
    def can_start_task(self, task: Task) -> bool:
        """작업 시작 가능 여부 확인"""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    async def execute_task(self, task: Task):
        """개별 작업 실행"""
        task.status = TaskStatus.IN_PROGRESS
        task.start_time = datetime.now()
        self.print_progress(task)
        
        try:
            # 실제 작업 수행
            if task.command:
                # 명령어 실행
                result = subprocess.run(task.command, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(f"Command failed: {result.stderr}")
                task.result = result.stdout
            
            # 파일 생성 표시
            if task.files_to_create:
                for file_path in task.files_to_create:
                    print(f"  → 파일 생성 예정: {file_path}")
            
            # 진행률 업데이트
            task.progress = 100
            task.status = TaskStatus.COMPLETED
            task.end_time = datetime.now()
            
            self.print_progress(task)
            logger.info(f"작업 완료: {task.name}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.end_time = datetime.now()
            self.print_progress(task)
            logger.error(f"작업 실패: {task.name} - {e}")
    
    async def run(self):
        """작업 관리자 실행"""
        self.is_running = True
        
        print("\n" + "="*80)
        print("HR 대시보드 구현 작업 시작".center(80))
        print("="*80 + "\n")
        
        print(f"총 작업 수: {len(self.tasks)}")
        print("\n작업 목록:")
        for task_id, task in self.tasks.items():
            print(f"  - [{task.task_type.value}] {task.name}")
        print("\n")
        
        try:
            while self.is_running:
                # 실행 가능한 작업 찾기
                pending_tasks = [
                    task for task in self.tasks.values()
                    if task.status == TaskStatus.PENDING and self.can_start_task(task)
                ]
                
                if not pending_tasks:
                    # 모든 작업 완료 확인
                    incomplete_tasks = [
                        task for task in self.tasks.values()
                        if task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                    ]
                    
                    if not incomplete_tasks:
                        print("\n모든 작업 완료!")
                        break
                    
                    await asyncio.sleep(1)
                    continue
                
                # 작업 실행
                for task in pending_tasks:
                    await self.execute_task(task)
        
        finally:
            # 완료 통계
            print("\n" + "="*80)
            print("작업 완료 통계".center(80))
            print("="*80)
            print(f"전체 진행률: {self.calculate_overall_progress():.1f}%")
            print(f"성공: {sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)}")
            print(f"실패: {sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)}")
            print("="*80 + "\n")
            
            self.is_running = False


async def main():
    """메인 실행 함수"""
    manager = HRDashboardTaskManager()
    await manager.run()


if __name__ == "__main__":
    asyncio.run(main())