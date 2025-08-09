"""
AI 통합 테스트 관리 명령어
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from employees.models import Employee
from ai_quickwin.services import AIQuickWinOrchestrator
import json


class Command(BaseCommand):
    help = 'AI 모듈 통합 테스트 및 검증'

    def add_arguments(self, parser):
        parser.add_argument(
            '--employee-id',
            type=int,
            help='테스트할 직원 ID',
        )
        parser.add_argument(
            '--module',
            type=str,
            choices=['all', 'airiss', 'insights', 'predictions', 'coaching', 'team', 'interviewer'],
            default='all',
            help='테스트할 모듈 선택',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='상세 출력 모드',
        )

    def handle(self, *args, **options):
        orchestrator = AIQuickWinOrchestrator()
        employee_id = options.get('employee_id')
        module = options.get('module')
        verbose = options.get('verbose')

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('AI 통합 테스트 시작'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # 1. 모듈 상태 체크
        self.stdout.write('\n📊 모듈 상태 확인...')
        status = orchestrator.get_module_integration_status()
        
        if verbose:
            self.stdout.write(json.dumps(status, indent=2, ensure_ascii=False))
        
        self.stdout.write(f"통합 상태: {status['integration_health']}")
        self.stdout.write(f"활성 모듈: {status['summary']['active_modules']}/{status['summary']['total_modules']}")
        
        # 2. 직원 프로파일 동기화 테스트
        if employee_id:
            self.stdout.write(f'\n🔄 직원 #{employee_id} 프로파일 동기화 테스트...')
            
            try:
                employee = Employee.objects.get(id=employee_id)
                self.stdout.write(f"직원 정보: {employee.name} ({employee.position})")
                
                # 동기화 실행
                sync_result = orchestrator.sync_employee_profile(employee_id)
                
                if sync_result['success']:
                    self.stdout.write(self.style.SUCCESS('✅ 동기화 성공!'))
                    if verbose:
                        self.stdout.write(f"분석 결과:")
                        self.stdout.write(f"  - 이직 위험도: {sync_result['analysis_summary']['turnover_risk_score']}")
                        self.stdout.write(f"  - 승진 가능성: {sync_result['analysis_summary']['promotion_potential_score']}")
                        self.stdout.write(f"  - 동기화된 모듈: {', '.join(sync_result['synced_modules'])}")
                else:
                    self.stdout.write(self.style.ERROR(f"❌ 동기화 실패: {sync_result.get('error')}"))
                    
            except Employee.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"직원 #{employee_id}을(를) 찾을 수 없습니다"))
        
        # 3. 종합 리포트 생성 테스트
        if employee_id and module in ['all', 'report']:
            self.stdout.write(f'\n📄 종합 리포트 생성 테스트...')
            
            report = orchestrator.generate_comprehensive_report(employee_id)
            
            if 'error' not in report:
                self.stdout.write(self.style.SUCCESS('✅ 리포트 생성 성공!'))
                
                if verbose:
                    self.stdout.write('\n리포트 요약:')
                    if 'summary' in report:
                        self.stdout.write(f"  - 전체 상태: {report['summary']['overall_status']}")
                        self.stdout.write(f"  - 주요 인사이트: {len(report['summary']['key_insights'])}개")
                        self.stdout.write(f"  - 즉시 조치 필요: {len(report['summary']['immediate_actions'])}개")
            else:
                self.stdout.write(self.style.ERROR(f"❌ 리포트 생성 실패: {report['error']}"))
        
        # 4. 개별 모듈 테스트
        if module != 'all':
            self.stdout.write(f'\n🧪 {module} 모듈 개별 테스트...')
            # 모듈별 세부 테스트 로직 추가 가능
            
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('테스트 완료'))
        self.stdout.write(self.style.SUCCESS('=' * 60))