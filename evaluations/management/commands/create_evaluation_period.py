from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from evaluations.models import EvaluationPeriod


class Command(BaseCommand):
    help = '활성 평가 기간을 생성합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            default='2024년 하반기 평가',
            help='평가 기간 이름'
        )
        parser.add_argument(
            '--days-before',
            type=int,
            default=30,
            help='오늘로부터 며칠 전부터 시작'
        )
        parser.add_argument(
            '--days-after',
            type=int,
            default=60,
            help='오늘로부터 며칠 후까지'
        )

    def handle(self, *args, **options):
        # 기존 활성 평가 기간이 있는지 확인
        active_period = EvaluationPeriod.objects.filter(is_active=True).first()
        
        if active_period:
            self.stdout.write(
                self.style.WARNING(f'이미 활성 평가 기간이 있습니다: {active_period.name}')
            )
            self.stdout.write(f'기간: {active_period.start_date} ~ {active_period.end_date}')
            return
        
        # 새 평가 기간 생성
        today = date.today()
        start_date = today - timedelta(days=options['days_before'])
        end_date = today + timedelta(days=options['days_after'])
        
        period = EvaluationPeriod.objects.create(
            name=options['name'],
            year=today.year,
            period_type='H2' if today.month > 6 else 'H1',  # 하반기/상반기 자동 설정
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            status='ONGOING',
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ 새 평가 기간이 생성되었습니다: {period.name}')
        )
        self.stdout.write(f'기간: {period.start_date} ~ {period.end_date}')
        self.stdout.write(f'활성 상태: {"✓ 활성" if period.is_active else "비활성"}')
        
        # 기존의 다른 평가 기간들은 비활성화
        deactivated = EvaluationPeriod.objects.exclude(id=period.id).update(is_active=False)
        if deactivated > 0:
            self.stdout.write(
                self.style.SUCCESS(f'{deactivated}개의 다른 평가 기간이 비활성화되었습니다.')
            )
        
        # 모든 평가 기간 출력
        self.stdout.write('\n📊 현재 평가 기간 목록:')
        for p in EvaluationPeriod.objects.all().order_by('-is_active', '-start_date'):
            status = '🟢 활성' if p.is_active else '⚪ 비활성'
            self.stdout.write(
                f'  {status} | {p.name} | {p.start_date} ~ {p.end_date}'
            )