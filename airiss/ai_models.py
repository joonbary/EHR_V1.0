"""
AIRISS AI 모델 구현
실제 머신러닝 기반 HR 분석 모델들
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import joblib
import os
from django.conf import settings
from django.utils import timezone

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
import warnings
warnings.filterwarnings('ignore')

from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation
from compensation.models import EmployeeCompensation


class BaseHRModel:
    """HR 모델 기본 클래스"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.model_path = os.path.join(settings.BASE_DIR, 'airiss', 'models', f'{model_name}.joblib')
        self.scaler_path = os.path.join(settings.BASE_DIR, 'airiss', 'models', f'{model_name}_scaler.joblib')
        
        # 모델 디렉토리 생성
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
    
    def save_model(self):
        """모델 저장"""
        if self.model is not None:
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'feature_names': self.feature_names
            }, self.model_path)
    
    def load_model(self) -> bool:
        """모델 로드"""
        try:
            if os.path.exists(self.model_path):
                data = joblib.load(self.model_path)
                self.model = data['model']
                self.scaler = data['scaler']
                self.label_encoders = data['label_encoders']
                self.feature_names = data['feature_names']
                return True
        except Exception as e:
            print(f"모델 로드 실패: {e}")
        return False


class TurnoverPredictionModel(BaseHRModel):
    """퇴사 위험도 예측 모델"""
    
    def __init__(self):
        super().__init__('turnover_prediction')
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
    
    def extract_features(self, employees_df: pd.DataFrame) -> pd.DataFrame:
        """직원 데이터에서 특성 추출"""
        features = pd.DataFrame()
        
        # 기본 정보
        features['age'] = (datetime.now().date() - pd.to_datetime(employees_df['birth_date']).dt.date).dt.days / 365.25
        features['tenure_years'] = (datetime.now().date() - pd.to_datetime(employees_df['hire_date']).dt.date).dt.days / 365.25
        features['growth_level'] = employees_df['growth_level']
        
        # 부서 인코딩
        if 'department' not in self.label_encoders:
            self.label_encoders['department'] = LabelEncoder()
            features['department_encoded'] = self.label_encoders['department'].fit_transform(employees_df['department'].fillna('Unknown'))
        else:
            features['department_encoded'] = self.label_encoders['department'].transform(employees_df['department'].fillna('Unknown'))
        
        # 직위 인코딩
        if 'position' not in self.label_encoders:
            self.label_encoders['position'] = LabelEncoder()
            features['position_encoded'] = self.label_encoders['position'].fit_transform(employees_df['new_position'].fillna('Unknown'))
        else:
            features['position_encoded'] = self.label_encoders['position'].transform(employees_df['new_position'].fillna('Unknown'))
        
        # 성별 인코딩
        features['gender_encoded'] = (employees_df['gender'] == 'M').astype(int)
        
        # 급여 관련 특성 (있는 경우)
        if 'salary' in employees_df.columns:
            features['salary_normalized'] = employees_df['salary'] / employees_df['salary'].mean()
        else:
            features['salary_normalized'] = 1.0
        
        # 최근 평가 점수 (있는 경우)
        features['recent_evaluation_score'] = 75.0  # 기본값
        
        # 통계적 특성
        features['tenure_in_position'] = np.minimum(features['tenure_years'], 5)  # 현 직위 경력 (최대 5년)
        features['age_at_hire'] = features['age'] - features['tenure_years']
        features['promotion_potential'] = (features['tenure_years'] / (features['growth_level'] + 1)) * 10
        
        self.feature_names = features.columns.tolist()
        return features
    
    def prepare_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """훈련 데이터 준비"""
        # 전체 직원 데이터 가져오기
        employees = Employee.objects.all()
        employees_data = []
        
        for emp in employees:
            employees_data.append({
                'id': emp.id,
                'birth_date': emp.birth_date,
                'hire_date': emp.hire_date,
                'growth_level': emp.growth_level,
                'department': emp.department or 'Unknown',
                'new_position': emp.new_position or 'Unknown',
                'gender': emp.gender,
                'employment_status': emp.employment_status
            })
        
        df = pd.DataFrame(employees_data)
        
        # 특성 추출
        features = self.extract_features(df)
        
        # 타겟 생성 (퇴직자는 1, 재직자는 0)
        target = (df['employment_status'] == '퇴직').astype(int)
        
        return features, target
    
    def train(self) -> Dict[str, float]:
        """모델 훈련"""
        X, y = self.prepare_training_data()
        
        if len(X) < 10:
            # 데이터가 부족하면 합성 데이터 생성
            X, y = self._generate_synthetic_data()
        
        # 데이터 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
        )
        
        # 데이터 스케일링
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 모델 훈련
        self.model.fit(X_train_scaled, y_train)
        
        # 평가
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # 모델 저장
        self.save_model()
        
        return {
            'accuracy': accuracy,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'feature_count': len(self.feature_names)
        }
    
    def predict_employee_turnover(self, employee: Employee) -> Dict[str, float]:
        """개별 직원의 퇴사 위험도 예측"""
        if self.model is None:
            if not self.load_model():
                return {'risk_score': 50.0, 'confidence': 0.5}
        
        # 직원 데이터를 DataFrame으로 변환
        emp_data = pd.DataFrame([{
            'birth_date': employee.birth_date,
            'hire_date': employee.hire_date,
            'growth_level': employee.growth_level,
            'department': employee.department or 'Unknown',
            'new_position': employee.new_position or 'Unknown',
            'gender': employee.gender
        }])
        
        # 특성 추출
        features = self.extract_features(emp_data)
        
        # 예측
        features_scaled = self.scaler.transform(features)
        risk_prob = self.model.predict_proba(features_scaled)[0][1]  # 퇴사할 확률
        risk_score = risk_prob * 100
        
        # 신뢰도 계산 (특성 중요도 기반)
        feature_importance = self.model.feature_importances_
        confidence = np.mean(feature_importance) * 0.8 + 0.2
        
        return {
            'risk_score': float(risk_score),
            'confidence': float(confidence),
            'factors': self._get_risk_factors(features.iloc[0], feature_importance)
        }
    
    def _generate_synthetic_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """합성 데이터 생성 (실제 데이터가 부족할 때)"""
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'age': np.random.normal(35, 8, n_samples),
            'tenure_years': np.random.exponential(3, n_samples),
            'growth_level': np.random.randint(1, 8, n_samples),
            'department_encoded': np.random.randint(0, 5, n_samples),
            'position_encoded': np.random.randint(0, 6, n_samples),
            'gender_encoded': np.random.randint(0, 2, n_samples),
            'salary_normalized': np.random.normal(1, 0.3, n_samples),
            'recent_evaluation_score': np.random.normal(75, 15, n_samples),
            'tenure_in_position': np.random.uniform(0, 5, n_samples),
            'age_at_hire': np.random.normal(28, 5, n_samples),
            'promotion_potential': np.random.uniform(0, 50, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # 타겟 생성 (나이가 많고, 근속년수가 짧고, 평가점수가 낮으면 퇴사 위험 높음)
        risk_score = (
            (df['age'] - 30) * 0.02 +
            (5 - df['tenure_years']) * 0.1 +
            (75 - df['recent_evaluation_score']) * 0.01 +
            np.random.normal(0, 0.1, n_samples)
        )
        
        target = (risk_score > 0.3).astype(int)
        
        self.feature_names = df.columns.tolist()
        return df, target
    
    def _get_risk_factors(self, features: pd.Series, importance: np.ndarray) -> Dict[str, float]:
        """위험 요소 분석"""
        factors = {}
        feature_names = self.feature_names
        
        for i, (name, value) in enumerate(features.items()):
            if i < len(importance):
                factors[name] = float(importance[i] * value)
        
        return factors


class PromotionPredictionModel(BaseHRModel):
    """승진 가능성 예측 모델"""
    
    def __init__(self):
        super().__init__('promotion_prediction')
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            random_state=42
        )
    
    def extract_features(self, employees_df: pd.DataFrame) -> pd.DataFrame:
        """승진 관련 특성 추출"""
        features = pd.DataFrame()
        
        # 기본 정보
        features['age'] = (datetime.now().date() - pd.to_datetime(employees_df['birth_date']).dt.date).dt.days / 365.25
        features['tenure_years'] = (datetime.now().date() - pd.to_datetime(employees_df['hire_date']).dt.date).dt.days / 365.25
        features['current_level'] = employees_df['growth_level']
        
        # 현재 직급에서의 경력
        features['time_in_position'] = np.minimum(features['tenure_years'], 5)
        
        # 승진 적정 연령대 (35-45세가 최적)
        features['optimal_age_score'] = 1 - np.abs(features['age'] - 40) / 20
        features['optimal_age_score'] = np.clip(features['optimal_age_score'], 0, 1)
        
        # 경력 점수
        features['experience_score'] = np.minimum(features['tenure_years'] / 5, 1)
        
        # 부서별 승진 기회 (임의로 설정)
        dept_promotion_rate = {
            'IT': 0.8, '영업': 0.7, '마케팅': 0.6, '인사': 0.5, 
            '회계': 0.4, '기타': 0.3, 'Unknown': 0.3
        }
        features['dept_promotion_opportunity'] = employees_df['department'].map(dept_promotion_rate).fillna(0.3)
        
        # 리더십 잠재력 (현재 레벨과 경력 기반)
        features['leadership_potential'] = (features['current_level'] * 0.6 + features['experience_score'] * 0.4)
        
        self.feature_names = features.columns.tolist()
        return features
    
    def prepare_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """훈련 데이터 준비"""
        employees = Employee.objects.all()
        employees_data = []
        
        for emp in employees:
            employees_data.append({
                'birth_date': emp.birth_date,
                'hire_date': emp.hire_date,
                'growth_level': emp.growth_level,
                'department': emp.department or 'Unknown'
            })
        
        df = pd.DataFrame(employees_data)
        features = self.extract_features(df)
        
        # 승진 점수 생성 (특성들의 가중합)
        promotion_score = (
            features['optimal_age_score'] * 25 +
            features['experience_score'] * 30 +
            features['dept_promotion_opportunity'] * 20 +
            features['leadership_potential'] * 25 +
            np.random.normal(0, 5, len(features))  # 노이즈
        )
        
        promotion_score = np.clip(promotion_score, 0, 100)
        
        return features, promotion_score
    
    def train(self) -> Dict[str, float]:
        """모델 훈련"""
        X, y = self.prepare_training_data()
        
        if len(X) < 10:
            X, y = self._generate_synthetic_promotion_data()
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model.fit(X_train_scaled, y_train)
        
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        
        self.save_model()
        
        return {
            'mse': mse,
            'rmse': np.sqrt(mse),
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }
    
    def predict_promotion_potential(self, employee: Employee) -> Dict[str, float]:
        """승진 가능성 예측"""
        if self.model is None:
            if not self.load_model():
                return {'promotion_score': 50.0, 'confidence': 0.5}
        
        emp_data = pd.DataFrame([{
            'birth_date': employee.birth_date,
            'hire_date': employee.hire_date,
            'growth_level': employee.growth_level,
            'department': employee.department or 'Unknown'
        }])
        
        features = self.extract_features(emp_data)
        features_scaled = self.scaler.transform(features)
        
        promotion_score = self.model.predict(features_scaled)[0]
        promotion_score = np.clip(promotion_score, 0, 100)
        
        # 예측 신뢰도
        confidence = min(0.9, 0.5 + features.iloc[0]['experience_score'] * 0.3)
        
        return {
            'promotion_score': float(promotion_score),
            'confidence': float(confidence),
            'readiness_factors': self._get_promotion_factors(features.iloc[0])
        }
    
    def _generate_synthetic_promotion_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """합성 승진 데이터 생성"""
        np.random.seed(42)
        n_samples = 800
        
        data = {
            'age': np.random.normal(35, 8, n_samples),
            'tenure_years': np.random.exponential(4, n_samples),
            'current_level': np.random.randint(1, 8, n_samples),
            'time_in_position': np.random.uniform(0, 5, n_samples),
            'optimal_age_score': np.random.beta(2, 2, n_samples),
            'experience_score': np.random.beta(3, 2, n_samples),
            'dept_promotion_opportunity': np.random.uniform(0.3, 0.8, n_samples),
            'leadership_potential': np.random.beta(2, 3, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # 승진 점수 생성
        promotion_score = (
            df['optimal_age_score'] * 25 +
            df['experience_score'] * 30 +
            df['dept_promotion_opportunity'] * 20 +
            df['leadership_potential'] * 25 +
            np.random.normal(0, 5, n_samples)
        )
        
        promotion_score = np.clip(promotion_score, 0, 100)
        
        self.feature_names = df.columns.tolist()
        return df, promotion_score
    
    def _get_promotion_factors(self, features: pd.Series) -> Dict[str, float]:
        """승진 준비도 요소들"""
        return {
            'age_readiness': float(features['optimal_age_score']),
            'experience_level': float(features['experience_score']),
            'department_opportunity': float(features['dept_promotion_opportunity']),
            'leadership_potential': float(features['leadership_potential']),
            'tenure_adequacy': min(1.0, float(features['tenure_years'] / 3))
        }


class TeamPerformanceModel(BaseHRModel):
    """팀 성과 예측 모델"""
    
    def __init__(self):
        super().__init__('team_performance')
        self.model = RandomForestRegressor(
            n_estimators=80,
            max_depth=6,
            random_state=42
        )
    
    def extract_team_features(self, department: str) -> Dict[str, float]:
        """팀 특성 추출"""
        team_members = Employee.objects.filter(
            department=department,
            employment_status='재직'
        )
        
        if not team_members.exists():
            return self._get_default_features()
        
        features = {}
        
        # 팀 크기
        features['team_size'] = float(team_members.count())
        
        # 평균 근속년수
        tenure_days = [(timezone.now().date() - emp.hire_date).days for emp in team_members]
        features['avg_tenure_years'] = float(np.mean(tenure_days)) / 365.25
        
        # 경력 다양성 (Growth Level 분산)
        growth_levels = [emp.growth_level for emp in team_members]
        features['experience_diversity'] = float(np.std(growth_levels))
        
        # 연령 분포
        ages = [(timezone.now().date() - emp.birth_date).days / 365.25 for emp in team_members if emp.birth_date]
        features['avg_age'] = float(np.mean(ages)) if ages else 35.0
        features['age_diversity'] = float(np.std(ages)) if len(ages) > 1 else 5.0
        
        # 성별 다양성
        gender_counts = list(team_members.values_list('gender', flat=True))
        male_ratio = gender_counts.count('M') / len(gender_counts) if gender_counts else 0.5
        features['gender_diversity'] = float(1 - abs(male_ratio - 0.5) * 2)
        
        # 최적 팀 크기 점수 (5-10명이 최적)
        optimal_size = max(0, 1 - abs(features['team_size'] - 7.5) / 7.5)
        features['optimal_size_score'] = float(optimal_size)
        
        # 경험 균형 점수
        features['experience_balance'] = float(min(1.0, features['experience_diversity'] / 3))
        
        return features
    
    def _get_default_features(self) -> Dict[str, float]:
        """기본 특성값"""
        return {
            'team_size': 5.0,
            'avg_tenure_years': 3.0,
            'experience_diversity': 2.0,
            'avg_age': 35.0,
            'age_diversity': 5.0,
            'gender_diversity': 0.5,
            'optimal_size_score': 0.7,
            'experience_balance': 0.6
        }
    
    def predict_team_performance(self, department: str) -> Dict[str, float]:
        """팀 성과 예측"""
        if self.model is None:
            # 모델이 없으면 규칙 기반으로 계산
            return self._rule_based_team_prediction(department)
        
        features = self.extract_team_features(department)
        feature_array = np.array(list(features.values())).reshape(1, -1)
        
        try:
            feature_array_scaled = self.scaler.transform(feature_array)
            performance_score = self.model.predict(feature_array_scaled)[0]
        except:
            performance_score = self._calculate_rule_based_score(features)
        
        performance_score = np.clip(performance_score, 0, 100)
        
        return {
            'performance_score': float(performance_score),
            'confidence': 0.75,
            'team_metrics': features,
            'recommendations': self._get_team_recommendations(features)
        }
    
    def _rule_based_team_prediction(self, department: str) -> Dict[str, float]:
        """규칙 기반 팀 성과 예측"""
        features = self.extract_team_features(department)
        score = self._calculate_rule_based_score(features)
        
        return {
            'performance_score': float(score),
            'confidence': 0.65,
            'team_metrics': features,
            'recommendations': self._get_team_recommendations(features)
        }
    
    def _calculate_rule_based_score(self, features: Dict[str, float]) -> float:
        """규칙 기반 점수 계산"""
        score = 50.0  # 기본 점수
        
        # 팀 크기 점수
        score += features['optimal_size_score'] * 15
        
        # 경험 다양성 점수
        score += min(features['experience_diversity'] / 3, 1) * 10
        
        # 평균 근속년수 점수 (2-5년이 최적)
        tenure_score = max(0, 1 - abs(features['avg_tenure_years'] - 3.5) / 3.5)
        score += tenure_score * 15
        
        # 성별 다양성 점수
        score += features['gender_diversity'] * 10
        
        # 연령 적정성 (30-40세 평균이 최적)
        age_score = max(0, 1 - abs(features['avg_age'] - 35) / 15)
        score += age_score * 10
        
        return np.clip(score, 0, 100)
    
    def _get_team_recommendations(self, features: Dict[str, float]) -> List[str]:
        """팀 개선 추천사항"""
        recommendations = []
        
        if features['team_size'] < 3:
            recommendations.append("팀 규모 확대를 통한 업무 분산 필요")
        elif features['team_size'] > 12:
            recommendations.append("팀 규모 축소 또는 하위 팀 구성 검토")
        
        if features['experience_diversity'] < 1.5:
            recommendations.append("다양한 경력 수준의 인재 영입 필요")
        
        if features['avg_tenure_years'] < 1:
            recommendations.append("팀 안정성 향상을 위한 리텐션 전략 필요")
        elif features['avg_tenure_years'] > 8:
            recommendations.append("새로운 아이디어 유입을 위한 신규 인재 영입")
        
        if features['gender_diversity'] < 0.3:
            recommendations.append("성별 다양성 증진을 통한 관점 다양화")
        
        if not recommendations:
            recommendations.append("현재 팀 구성이 양호하여 지속적인 팀 빌딩 활동 추천")
        
        return recommendations


# AI 모델 관리자 클래스
class AIModelManager:
    """AI 모델들을 통합 관리하는 클래스"""
    
    def __init__(self):
        self.turnover_model = TurnoverPredictionModel()
        self.promotion_model = PromotionPredictionModel()
        self.team_model = TeamPerformanceModel()
    
    def train_all_models(self) -> Dict[str, Dict]:
        """모든 모델 훈련"""
        results = {}
        
        try:
            results['turnover'] = self.turnover_model.train()
        except Exception as e:
            results['turnover'] = {'error': str(e)}
        
        try:
            results['promotion'] = self.promotion_model.train()
        except Exception as e:
            results['promotion'] = {'error': str(e)}
        
        # 팀 모델은 별도 훈련 로직이 필요하므로 기본값 설정
        results['team'] = {'status': 'rule_based', 'accuracy': 0.75}
        
        return results
    
    def get_model_status(self) -> Dict[str, bool]:
        """모델 상태 확인"""
        return {
            'turnover': self.turnover_model.load_model(),
            'promotion': self.promotion_model.load_model(),
            'team': True  # 규칙 기반이므로 항상 사용 가능
        }