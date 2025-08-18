"""
Railway 배포 시 데이터베이스를 안전하게 초기화하는 명령
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = 'Railway 데이터베이스를 안전하게 초기화합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='확인 없이 강제 실행',
        )

    def handle(self, *args, **options):
        # Railway 환경인지 확인
        is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
        
        if not is_railway and not options['force']:
            self.stdout.write(self.style.WARNING('Railway 환경이 아닙니다. --force 옵션을 사용하세요.'))
            return
        
        self.stdout.write(self.style.NOTICE('데이터베이스 초기화를 시작합니다...'))
        
        try:
            with connection.cursor() as cursor:
                # 테이블이 이미 존재하는지 확인
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    AND tablename NOT LIKE 'django_%'
                """)
                custom_table_count = cursor.fetchone()[0]
                
                if custom_table_count > 0:
                    self.stdout.write(f'기존 테이블 {custom_table_count}개 발견')
                    
                    # 기존 테이블 삭제
                    cursor.execute("""
                        DO $$ 
                        DECLARE
                            r RECORD;
                        BEGIN
                            -- 외래키 제약 조건 일시 비활성화
                            SET session_replication_role = 'replica';
                            
                            -- 모든 테이블 삭제
                            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
                            LOOP
                                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                            END LOOP;
                            
                            -- 외래키 제약 조건 다시 활성화
                            SET session_replication_role = 'origin';
                        END $$;
                    """)
                    self.stdout.write(self.style.SUCCESS('기존 테이블 삭제 완료'))
            
            # 마이그레이션 실행
            self.stdout.write('마이그레이션 실행 중...')
            call_command('migrate', '--run-syncdb', verbosity=0)
            self.stdout.write(self.style.SUCCESS('마이그레이션 완료'))
            
            # 검증
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                """)
                total_tables = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f'총 {total_tables}개의 테이블이 생성되었습니다'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'오류 발생: {e}'))
            raise