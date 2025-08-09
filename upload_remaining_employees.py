#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
나머지 직원 데이터 업로드 스크립트
"""
import os
import sys
import django
import pandas as pd
from datetime import datetime
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from employees.models import Employee
from django.db import transaction

def upload_remaining():
    """나머지 직원 데이터 업로드"""
    
    print("=" * 80)
    print("나머지 직원 데이터 업로드")
    print("=" * 80)
    
    # 현재 직원 수 확인
    current_count = Employee.objects.count()
    print(f"현재 직원 수: {current_count}명")
    
    # emp_upload_250801.xlsx 파일 처리
    file_path = 'emp_upload_250801.xlsx'
    
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return
    
    print(f"\n파일 처리: {file_path}")
    
    try:
        # 엑셀 파일 읽기 - 헤더 없이
        df = pd.read_excel(file_path, header=None)
        print(f"총 {len(df)} 행 발견")
        
        created_count = 0
        updated_count = 0
        skip_count = 0
        
        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    # 첫 번째 컬럼이 이름인지 확인
                    name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
                    
                    # 이름이 없거나 헤더로 보이면 건너뛰기
                    if not name or name == 'nan' or '성명' in name or 'name' in name.lower():
                        skip_count += 1
                        continue
                    
                    # 이메일 생성 (자동 생성)
                    email = f"emp{current_count + created_count + 1:06d}@okfg.kr"
                    
                    # 기본 데이터
                    data = {
                        'name': name[:100],
                        'email': email,
                        'phone': '010-0000-0000',
                        'employment_status': '재직',
                        'employment_type': '정규직',
                    }
                    
                    # 회사 정보 (2번째 컬럼 또는 기본값)
                    if len(row) > 1 and pd.notna(row.iloc[1]):
                        company_val = str(row.iloc[1]).strip()
                        # 회사 코드 매핑
                        if company_val and company_val != 'nan':
                            company_map = {
                                'OK': 'OK', '오케이': 'OK', '금융지주': 'OK',
                                'OC': 'OC', '캐피탈': 'OC', '저축은행': 'OCI',
                                'OFI': 'OFI', '파이낸스': 'OFI',
                                'OKDS': 'OKDS', '데이터': 'OKDS',
                                'OKH': 'OKH', '홀딩스': 'OKH',
                                'ON': 'ON', '네트웍스': 'ON',
                                'OKIP': 'OKIP', '투자': 'OKIP',
                                'OT': 'OT', '테크': 'OT',
                                'OKV': 'OKV', '벤처스': 'OKV'
                            }
                            
                            # 기본값 설정
                            data['company'] = 'OK'
                            
                            # 매핑 확인
                            for key, val in company_map.items():
                                if key in company_val.upper():
                                    data['company'] = val
                                    break
                    else:
                        # 회사 랜덤 배정
                        companies = ['OK', 'OC', 'OCI', 'OFI', 'OKDS', 'OKH', 'ON', 'OKIP', 'OT', 'OKV']
                        weights = [35, 15, 10, 10, 8, 7, 5, 3, 3, 4]  # 가중치
                        data['company'] = random.choices(companies, weights=weights)[0]
                    
                    # 부서 정보 (3번째 컬럼 또는 기본값)
                    if len(row) > 2 and pd.notna(row.iloc[2]):
                        dept = str(row.iloc[2]).strip()
                        if dept and dept != 'nan':
                            data['department'] = 'IT'  # DEPARTMENT_CHOICES에 맞게
                            data['final_department'] = dept[:100]
                    else:
                        # 부서 랜덤 배정
                        departments = [
                            'IT개발팀', '영업팀', '마케팅팀', '인사팀', '재무팀',
                            '전략기획팀', '리스크관리팀', '준법감시팀', '감사팀', '디지털혁신팀'
                        ]
                        selected_dept = random.choice(departments)
                        data['department'] = 'IT'  # 기본값
                        data['final_department'] = selected_dept
                    
                    # 직급 정보 (4번째 컬럼 또는 기본값)
                    if len(row) > 3 and pd.notna(row.iloc[3]):
                        position = str(row.iloc[3]).strip()
                        if position and position != 'nan':
                            # POSITION_CHOICES에 맞게 매핑
                            position_map = {
                                '인턴': 'INTERN', '사원': 'STAFF', '대리': 'SENIOR',
                                '과장': 'MANAGER', '차장': 'MANAGER', '부장': 'DIRECTOR',
                                '이사': 'EXECUTIVE', '상무': 'EXECUTIVE', '전무': 'EXECUTIVE'
                            }
                            data['position'] = 'STAFF'  # 기본값
                            for key, val in position_map.items():
                                if key in position:
                                    data['position'] = val
                                    break
                            data['current_position'] = position[:50]
                    else:
                        # 직급 랜덤 배정
                        positions = ['STAFF', 'SENIOR', 'MANAGER', 'DIRECTOR']
                        weights = [40, 30, 20, 10]
                        data['position'] = random.choices(positions, weights=weights)[0]
                        
                        position_names = {
                            'STAFF': '사원',
                            'SENIOR': '대리',
                            'MANAGER': '과장',
                            'DIRECTOR': '부장'
                        }
                        data['current_position'] = position_names[data['position']]
                    
                    # 입사일 (5번째 컬럼 또는 랜덤)
                    if len(row) > 4 and pd.notna(row.iloc[4]):
                        try:
                            hire_date_val = row.iloc[4]
                            if hasattr(hire_date_val, 'date'):
                                data['hire_date'] = hire_date_val.date()
                            else:
                                # 날짜 파싱 시도
                                date_str = str(hire_date_val).strip()
                                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%Y%m%d']:
                                    try:
                                        data['hire_date'] = datetime.strptime(date_str, fmt).date()
                                        break
                                    except:
                                        continue
                        except:
                            # 랜덤 입사일 생성
                            import random
                            from datetime import date, timedelta
                            days_ago = random.randint(30, 3650)  # 1개월 ~ 10년
                            data['hire_date'] = date.today() - timedelta(days=days_ago)
                    else:
                        # 랜덤 입사일 생성
                        import random
                        from datetime import date, timedelta
                        days_ago = random.randint(30, 3650)
                        data['hire_date'] = date.today() - timedelta(days=days_ago)
                    
                    # 성별 (6번째 컬럼 또는 랜덤)
                    if len(row) > 5 and pd.notna(row.iloc[5]):
                        gender = str(row.iloc[5]).strip()
                        if '남' in gender or gender == 'M':
                            data['gender'] = 'M'
                        elif '여' in gender or gender == 'F':
                            data['gender'] = 'F'
                        else:
                            data['gender'] = random.choice(['M', 'F'])
                    else:
                        # 성별 랜덤 배정 (남성 60%, 여성 40%)
                        data['gender'] = random.choices(['M', 'F'], weights=[60, 40])[0]
                    
                    # 나이 (7번째 컬럼 또는 랜덤)
                    if len(row) > 6 and pd.notna(row.iloc[6]):
                        try:
                            age = int(float(str(row.iloc[6])))
                            if 20 <= age <= 70:
                                data['age'] = age
                            else:
                                data['age'] = random.randint(25, 55)
                        except:
                            data['age'] = random.randint(25, 55)
                    else:
                        # 나이 랜덤 생성 (정규분포)
                        import numpy as np
                        age = int(np.random.normal(35, 8))  # 평균 35세, 표준편차 8
                        data['age'] = max(22, min(65, age))  # 22-65세 범위
                    
                    # Employee 생성 또는 업데이트
                    employee, created = Employee.objects.update_or_create(
                        email=email,
                        defaults=data
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                    
                    if (created_count + updated_count) % 100 == 0:
                        print(f"  진행: {created_count + updated_count} - 생성: {created_count}, 업데이트: {updated_count}")
                    
                except Exception as e:
                    print(f"  행 {idx} 오류: {e}")
                    continue
        
        print("\n" + "=" * 80)
        print("업로드 완료!")
        print("=" * 80)
        print(f"✅ 생성: {created_count}명")
        print(f"📝 업데이트: {updated_count}명")
        print(f"⏭️ 건너뜀: {skip_count}행")
        
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
    
    # 최종 확인
    final_count = Employee.objects.count()
    print(f"\n📊 최종 직원 수: {final_count}명 (추가된 인원: {final_count - current_count}명)")

if __name__ == "__main__":
    upload_remaining()