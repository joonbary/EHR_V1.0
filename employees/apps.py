from django.apps import AppConfig
import os


class EmployeesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "employees"
    
    def ready(self):
        """앱 시작 시 필요한 테이블 자동 생성"""
        # Railway 환경에서만 실행
        if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('DATABASE_URL'):
            from django.db import connection
            
            try:
                with connection.cursor() as cursor:
                    # OrganizationStructure 테이블 확인 및 생성
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'employees_organizationstructure'
                        );
                    """)
                    
                    if not cursor.fetchone()[0]:
                        print("[AUTO] Creating OrganizationStructure tables...")
                        
                        # 1. OrganizationStructure 테이블
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS employees_organizationstructure (
                                id SERIAL PRIMARY KEY,
                                org_code VARCHAR(50) UNIQUE NOT NULL,
                                org_name VARCHAR(100) NOT NULL,
                                org_level INTEGER NOT NULL DEFAULT 1,
                                parent_id INTEGER REFERENCES employees_organizationstructure(id) ON DELETE CASCADE,
                                full_path VARCHAR(500) DEFAULT '',
                                group_name VARCHAR(100) DEFAULT '',
                                company_name VARCHAR(100) DEFAULT '',
                                headquarters_name VARCHAR(100) DEFAULT '',
                                department_name VARCHAR(100) DEFAULT '',
                                team_name VARCHAR(100) DEFAULT '',
                                description TEXT DEFAULT '',
                                establishment_date DATE,
                                status VARCHAR(20) DEFAULT 'active',
                                leader_id INTEGER,
                                sort_order INTEGER DEFAULT 0,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                created_by_id INTEGER
                            )
                        """)
                        
                        # 2. OrganizationUploadHistory 테이블
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS employees_organizationuploadhistory (
                                id SERIAL PRIMARY KEY,
                                file_name VARCHAR(255) NOT NULL,
                                file_path VARCHAR(100),
                                status VARCHAR(20) DEFAULT 'pending',
                                total_rows INTEGER DEFAULT 0,
                                processed_rows INTEGER DEFAULT 0,
                                success_count INTEGER DEFAULT 0,
                                error_count INTEGER DEFAULT 0,
                                error_details JSONB DEFAULT '[]'::jsonb,
                                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                processed_at TIMESTAMP,
                                uploaded_by_id INTEGER,
                                options JSONB DEFAULT '{}'::jsonb
                            )
                        """)
                        
                        # 3. EmployeeOrganizationMapping 테이블
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS employees_employeeorganizationmapping (
                                id SERIAL PRIMARY KEY,
                                employee_id INTEGER NOT NULL,
                                organization_id INTEGER NOT NULL REFERENCES employees_organizationstructure(id) ON DELETE CASCADE,
                                is_primary BOOLEAN DEFAULT TRUE,
                                role VARCHAR(50),
                                start_date DATE DEFAULT CURRENT_DATE,
                                end_date DATE,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """)
                        
                        # 4. Employee 테이블에 organization_id 추가
                        cursor.execute("""
                            ALTER TABLE employees_employee 
                            ADD COLUMN IF NOT EXISTS organization_id INTEGER
                        """)
                        
                        # 5. 인덱스 생성
                        cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_code ON employees_organizationstructure(org_code);")
                        cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_level_status ON employees_organizationstructure(org_level, status);")
                        cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_parent ON employees_organizationstructure(parent_id);")
                        
                        # 6. 마이그레이션 레코드 추가
                        cursor.execute("""
                            INSERT INTO django_migrations (app, name, applied) 
                            VALUES ('employees', '0003_organizationstructure_employeeorganizationmapping_and_more', CURRENT_TIMESTAMP)
                            ON CONFLICT DO NOTHING
                        """)
                        
                        # 7. 초기 데이터 추가
                        cursor.execute("""
                            INSERT INTO employees_organizationstructure 
                            (org_code, org_name, org_level, status, sort_order, group_name, full_path) 
                            VALUES ('GRP001', 'OK금융그룹', 1, 'active', 1, 'OK금융그룹', 'OK금융그룹')
                            ON CONFLICT (org_code) DO NOTHING
                        """)
                        
                        connection.commit()
                        print("[AUTO] OrganizationStructure tables created successfully!")
                        
            except Exception as e:
                print(f"[AUTO] Error creating tables: {e}")
                # 오류가 발생해도 앱 시작은 계속되도록 함
                pass