"""
Shrimp Task Manager - UI/UX 업그레이드 작업 관리자
WebSocket을 통한 실시간 진행상황 전송
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import websockets
import aiofiles

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
    PLANNING = "planning"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"


class Task:
    """개별 작업 클래스"""
    
    def __init__(self, 
                 task_id: str,
                 name: str,
                 description: str,
                 task_type: TaskType,
                 dependencies: List[str] = None,
                 estimated_time: int = 60):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.task_type = task_type
        self.dependencies = dependencies or []
        self.estimated_time = estimated_time  # seconds
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
            'estimated_time': self.estimated_time,
            'dependencies': self.dependencies,
            'result': self.result,
            'error': self.error
        }


class ShrimpTaskManager:
    """UI/UX 업그레이드 작업 관리자"""
    
    def __init__(self, websocket_url: str = "ws://localhost:8765"):
        self.websocket_url = websocket_url
        self.tasks: Dict[str, Task] = {}
        self.websocket = None
        self.is_running = False
        self._create_tasks()
    
    def _create_tasks(self):
        """UI/UX 업그레이드 작업 목록 생성"""
        tasks_data = [
            # Phase 1: Planning & Design
            {
                'task_id': 'plan_1',
                'name': 'UI/UX 업그레이드 계획 수립',
                'description': '전체 UI/UX 재설계 계획 수립 및 요구사항 분석',
                'task_type': TaskType.PLANNING,
                'estimated_time': 120
            },
            {
                'task_id': 'design_1',
                'name': '디자인 시스템 및 색상 팔레트 정의',
                'description': 'Primary #1443FF, Accent #FFD700 기반 색상 시스템 구축',
                'task_type': TaskType.DESIGN,
                'dependencies': ['plan_1'],
                'estimated_time': 90
            },
            {
                'task_id': 'design_2',
                'name': 'Tailwind CSS 설정 및 커스터마이징',
                'description': 'Tailwind 설정 파일 생성 및 커스텀 테마 구성',
                'task_type': TaskType.DESIGN,
                'dependencies': ['design_1'],
                'estimated_time': 60
            },
            
            # Phase 2: Layout Implementation
            {
                'task_id': 'impl_1',
                'name': '레이아웃 컴포넌트 생성 (MainLayout, AdminLayout)',
                'description': '상단 헤더 + 좌측 사이드바 + 콘텐츠 그리드 구현',
                'task_type': TaskType.IMPLEMENTATION,
                'dependencies': ['design_2'],
                'estimated_time': 180
            },
            {
                'task_id': 'impl_2',
                'name': '공통 UI 컴포넌트 라이브러리 구축',
                'description': 'Button, Input, Select, Card, DataTable 등 shadcn/ui 컴포넌트',
                'task_type': TaskType.IMPLEMENTATION,
                'dependencies': ['impl_1'],
                'estimated_time': 240
            },
            
            # Phase 3: Page Templates
            {
                'task_id': 'impl_3',
                'name': '페이지 템플릿 개발',
                'description': 'Dashboard, Profile, Evaluation, Organization, HRAdmin 페이지',
                'task_type': TaskType.IMPLEMENTATION,
                'dependencies': ['impl_2'],
                'estimated_time': 300
            },
            {
                'task_id': 'impl_4',
                'name': '다크모드 및 접근성 기능 구현',
                'description': 'WCAG 기준 준수 및 다크모드 토글 기능',
                'task_type': TaskType.IMPLEMENTATION,
                'dependencies': ['impl_3'],
                'estimated_time': 120
            },
            
            # Phase 4: Integration
            {
                'task_id': 'impl_5',
                'name': '기존 템플릿 업그레이드 및 통합',
                'description': 'Django 템플릿을 새로운 UI 시스템으로 마이그레이션',
                'task_type': TaskType.IMPLEMENTATION,
                'dependencies': ['impl_4'],
                'estimated_time': 180
            },
            
            # Phase 5: Testing & Deployment
            {
                'task_id': 'test_1',
                'name': '컴포넌트 테스트 및 검증',
                'description': '모든 UI 컴포넌트의 기능 및 접근성 테스트',
                'task_type': TaskType.TESTING,
                'dependencies': ['impl_5'],
                'estimated_time': 120
            },
            {
                'task_id': 'deploy_1',
                'name': '프로덕션 배포 준비',
                'description': '빌드 최적화 및 배포 스크립트 작성',
                'task_type': TaskType.DEPLOYMENT,
                'dependencies': ['test_1'],
                'estimated_time': 90
            }
        ]
        
        # Task 객체 생성
        for task_data in tasks_data:
            task = Task(**task_data)
            self.tasks[task.task_id] = task
    
    async def connect_websocket(self):
        """WebSocket 연결"""
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            logger.info(f"WebSocket 연결 성공: {self.websocket_url}")
            await self.send_message({
                'type': 'connection',
                'status': 'connected',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"WebSocket 연결 실패: {e}")
            self.websocket = None
    
    async def send_message(self, message: Dict[str, Any]):
        """WebSocket으로 메시지 전송"""
        if self.websocket:
            try:
                await self.websocket.send(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"메시지 전송 실패: {e}")
    
    async def send_progress_update(self, task: Task):
        """진행상황 업데이트 전송"""
        message = {
            'type': 'progress_update',
            'task': task.to_dict(),
            'overall_progress': self.calculate_overall_progress(),
            'timestamp': datetime.now().isoformat()
        }
        await self.send_message(message)
    
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
        await self.send_progress_update(task)
        
        try:
            # 작업 시뮬레이션 (실제 구현으로 대체 필요)
            steps = 10
            for i in range(steps):
                task.progress = ((i + 1) / steps) * 100
                await self.send_progress_update(task)
                
                # 실제 작업 수행 시뮬레이션
                await asyncio.sleep(task.estimated_time / steps)
            
            # 작업 완료
            task.status = TaskStatus.COMPLETED
            task.end_time = datetime.now()
            task.progress = 100
            task.result = f"{task.name} 완료"
            
            await self.send_progress_update(task)
            logger.info(f"작업 완료: {task.name}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.end_time = datetime.now()
            await self.send_progress_update(task)
            logger.error(f"작업 실패: {task.name} - {e}")
    
    async def run(self):
        """작업 관리자 실행"""
        self.is_running = True
        
        # WebSocket 연결
        await self.connect_websocket()
        
        # 시작 메시지 전송
        await self.send_message({
            'type': 'start',
            'total_tasks': len(self.tasks),
            'tasks': [task.to_dict() for task in self.tasks.values()],
            'timestamp': datetime.now().isoformat()
        })
        
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
                        logger.info("모든 작업 완료")
                        break
                    
                    # 대기
                    await asyncio.sleep(1)
                    continue
                
                # 병렬 실행 가능한 작업들 실행
                tasks_to_run = []
                for task in pending_tasks[:3]:  # 최대 3개 동시 실행
                    tasks_to_run.append(self.execute_task(task))
                
                await asyncio.gather(*tasks_to_run)
        
        finally:
            # 완료 메시지 전송
            await self.send_message({
                'type': 'complete',
                'overall_progress': self.calculate_overall_progress(),
                'success_count': sum(1 for t in self.tasks.values() 
                                   if t.status == TaskStatus.COMPLETED),
                'failed_count': sum(1 for t in self.tasks.values() 
                                  if t.status == TaskStatus.FAILED),
                'timestamp': datetime.now().isoformat()
            })
            
            # WebSocket 연결 종료
            if self.websocket:
                await self.websocket.close()
            
            self.is_running = False


async def main():
    """메인 실행 함수"""
    manager = ShrimpTaskManager()
    await manager.run()


if __name__ == "__main__":
    asyncio.run(main())