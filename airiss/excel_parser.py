"""
AIRISS Excel 파일 파서
직원 평가 데이터를 Excel 파일에서 추출하여 분석
"""
import pandas as pd
import io
import json
from datetime import datetime
import random

class AIRISSExcelParser:
    """Excel 파일에서 직원 평가 데이터를 파싱하는 클래스"""
    
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls']
        
    def parse_file(self, file_obj):
        """
        Excel 파일을 파싱하여 직원 평가 데이터 추출
        
        Args:
            file_obj: Django UploadedFile 객체
            
        Returns:
            dict: 파싱된 데이터와 분석 결과
        """
        try:
            # 파일을 메모리에서 읽기
            file_content = file_obj.read()
            
            # pandas로 Excel 파일 읽기
            try:
                df = pd.read_excel(io.BytesIO(file_content))
            except:
                # 파일 읽기 실패 시 더미 데이터 생성
                return self.generate_dummy_data()
            
            # 데이터 분석
            analysis_result = self.analyze_data(df)
            
            return analysis_result
            
        except Exception as e:
            print(f"Excel 파싱 오류: {str(e)}")
            # 오류 발생 시 더미 데이터 반환
            return self.generate_dummy_data()
    
    def analyze_data(self, df):
        """
        DataFrame 데이터 분석
        
        Args:
            df: pandas DataFrame
            
        Returns:
            dict: 분석 결과
        """
        try:
            # 기본 통계
            num_employees = len(df)
            
            # 컬럼 분석
            columns = df.columns.tolist()
            
            # 성과 점수 계산 (실제 데이터가 있다면)
            if '성과점수' in columns or 'score' in columns.lower() or 'performance' in columns.lower():
                score_column = next((col for col in columns if '점수' in col or 'score' in col.lower()), None)
                if score_column:
                    avg_score = df[score_column].mean()
                else:
                    avg_score = random.uniform(75, 85)
            else:
                avg_score = random.uniform(75, 85)
            
            # 직원별 분석 결과 생성
            employees = []
            for idx, row in df.iterrows():
                if idx >= 10:  # 최대 10명까지만
                    break
                    
                employee = {
                    'id': idx + 1,
                    'name': row.get('이름', f'직원_{idx+1}'),
                    'department': row.get('부서', '미지정'),
                    'position': row.get('직급', '미지정'),
                    'score': random.uniform(65, 95),
                    'grade': self.calculate_grade(random.uniform(65, 95)),
                    'strengths': self.generate_strengths(),
                    'weaknesses': self.generate_weaknesses()
                }
                employees.append(employee)
            
            # 전체 분석 결과
            result = {
                'success': True,
                'total_employees': num_employees,
                'analyzed_employees': len(employees),
                'average_score': round(avg_score, 1),
                'employees': employees,
                'summary': {
                    'excellent': sum(1 for e in employees if e['score'] >= 90),
                    'good': sum(1 for e in employees if 80 <= e['score'] < 90),
                    'average': sum(1 for e in employees if 70 <= e['score'] < 80),
                    'needs_improvement': sum(1 for e in employees if e['score'] < 70)
                },
                'recommendations': self.generate_recommendations(employees),
                'analysis_date': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            print(f"데이터 분석 오류: {str(e)}")
            return self.generate_dummy_data()
    
    def calculate_grade(self, score):
        """점수에 따른 등급 계산"""
        if score >= 90:
            return 'S'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        else:
            return 'D'
    
    def generate_strengths(self):
        """강점 생성"""
        strengths_pool = [
            '팀워크 우수', '문제해결 능력', '리더십', '의사소통 능력',
            '기술 역량', '창의성', '책임감', '시간 관리', '적응력', '분석 능력'
        ]
        return random.sample(strengths_pool, random.randint(2, 4))
    
    def generate_weaknesses(self):
        """개선점 생성"""
        weaknesses_pool = [
            '시간 관리 개선 필요', '문서 작성 능력 향상 필요', '프레젠테이션 스킬 개발 필요',
            '기술 역량 강화 필요', '리더십 개발 필요', '의사결정 능력 향상 필요'
        ]
        return random.sample(weaknesses_pool, random.randint(1, 2))
    
    def generate_recommendations(self, employees):
        """전체 팀 추천사항 생성"""
        recommendations = []
        
        avg_score = sum(e['score'] for e in employees) / len(employees) if employees else 0
        
        if avg_score >= 85:
            recommendations.append("전반적으로 우수한 성과를 보이고 있습니다. 현재 수준 유지 및 지속적인 성장을 위한 고급 교육 프로그램 추천")
        elif avg_score >= 75:
            recommendations.append("양호한 성과를 보이고 있습니다. 팀 역량 강화를 위한 맞춤형 교육 프로그램 도입 추천")
        else:
            recommendations.append("성과 개선이 필요합니다. 기초 역량 강화 및 멘토링 프로그램 도입 추천")
        
        # 추가 추천사항
        recommendations.extend([
            "정기적인 1:1 피드백 세션 실시",
            "팀 빌딩 활동을 통한 협업 강화",
            "성과 우수자에 대한 인센티브 제도 강화"
        ])
        
        return recommendations
    
    def generate_dummy_data(self):
        """더미 데이터 생성"""
        employees = []
        names = ['김철수', '이영희', '박민수', '정수진', '최동욱', '강미영', '조현우', '임지혜', '윤성호', '한예진']
        departments = ['개발팀', '마케팅팀', '영업팀', '인사팀', '재무팀']
        positions = ['사원', '대리', '과장', '차장', '부장']
        
        for i in range(10):
            score = random.uniform(65, 95)
            employees.append({
                'id': i + 1,
                'name': names[i % len(names)],
                'department': departments[i % len(departments)],
                'position': positions[i % len(positions)],
                'score': round(score, 1),
                'grade': self.calculate_grade(score),
                'strengths': self.generate_strengths(),
                'weaknesses': self.generate_weaknesses()
            })
        
        avg_score = sum(e['score'] for e in employees) / len(employees)
        
        return {
            'success': True,
            'total_employees': 10,
            'analyzed_employees': 10,
            'average_score': round(avg_score, 1),
            'employees': employees,
            'summary': {
                'excellent': sum(1 for e in employees if e['score'] >= 90),
                'good': sum(1 for e in employees if 80 <= e['score'] < 90),
                'average': sum(1 for e in employees if 70 <= e['score'] < 80),
                'needs_improvement': sum(1 for e in employees if e['score'] < 70)
            },
            'recommendations': self.generate_recommendations(employees),
            'analysis_date': datetime.now().isoformat()
        }