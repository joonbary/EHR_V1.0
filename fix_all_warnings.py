#!/usr/bin/env python
"""
Railway 배포 시 발생하는 모든 경고 및 오류 수정
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway 경고 및 오류 통합 수정")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

def fix_openai_proxies():
    """OpenAI proxies 문제 수정"""
    print("1. OpenAI API 설정 수정")
    print("-" * 40)
    
    # ai_feedback.py 수정
    ai_feedback_path = os.path.join(os.path.dirname(__file__), 'evaluations', 'ai_feedback.py')
    
    if os.path.exists(ai_feedback_path):
        with open(ai_feedback_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # proxies 파라미터 제거
        if 'proxies=' in content:
            content = content.replace('proxies=proxies,', '')
            content = content.replace('proxies=proxies', '')
            
            # 새로운 OpenAI 클라이언트 생성 방식으로 변경
            if 'OpenAI(' in content:
                old_pattern = "client = OpenAI(api_key=api_key, proxies=proxies)"
                new_pattern = "client = OpenAI(api_key=api_key)"
                content = content.replace(old_pattern, new_pattern)
                
                # proxies 변수 정의 부분도 주석 처리
                content = content.replace(
                    "proxies = {'http': http_proxy, 'https': https_proxy}",
                    "# proxies = {'http': http_proxy, 'https': https_proxy}  # OpenAI v1에서 지원 안함"
                )
            
            with open(ai_feedback_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("[OK] OpenAI proxies 문제 수정")
        else:
            print("[INFO] OpenAI proxies 이미 수정됨")
    else:
        print("[WARNING] ai_feedback.py 파일 없음")

def fix_team_recommendation():
    """TeamRecommendation 모델 누락 문제 수정"""
    print("\n2. TeamRecommendation 모델 생성")
    print("-" * 40)
    
    models_path = os.path.join(os.path.dirname(__file__), 'ai_team_optimizer', 'models.py')
    
    if os.path.exists(models_path):
        with open(models_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'class TeamRecommendation' not in content:
            # TeamRecommendation 모델 추가
            new_model = '''

class TeamRecommendation(models.Model):
    """팀 추천 모델"""
    team_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    recommended_for = models.CharField(max_length=200, blank=True)
    score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_team_recommendation'
        ordering = ['-score', '-created_at']
    
    def __str__(self):
        return f"{self.team_name} (Score: {self.score})"
'''
            content += new_model
            
            with open(models_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("[OK] TeamRecommendation 모델 추가")
        else:
            print("[INFO] TeamRecommendation 모델 이미 존재")
    else:
        # 디렉토리와 파일 생성
        os.makedirs(os.path.dirname(models_path), exist_ok=True)
        
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write('''from django.db import models

class TeamRecommendation(models.Model):
    """팀 추천 모델"""
    team_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    recommended_for = models.CharField(max_length=200, blank=True)
    score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_team_recommendation'
        ordering = ['-score', '-created_at']
    
    def __str__(self):
        return f"{self.team_name} (Score: {self.score})"
''')
        print("[OK] ai_team_optimizer/models.py 생성")

def fix_anthropic_client():
    """Anthropic client 초기화 문제 수정"""
    print("\n3. Anthropic API 설정 수정")
    print("-" * 40)
    
    services_path = os.path.join(os.path.dirname(__file__), 'ai_quickwin', 'services.py')
    
    if os.path.exists(services_path):
        with open(services_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # try-except으로 감싸기
        if 'anthropic.Client' in content or 'anthropic.Anthropic' in content:
            # 안전한 초기화로 변경
            old_pattern = "client = anthropic.Client(api_key=api_key)"
            new_pattern = """try:
        client = anthropic.Anthropic(api_key=api_key) if api_key else None
    except Exception as e:
        logger.warning(f"Anthropic client initialization failed: {e}")
        client = None"""
            
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
            
            # import 문 수정
            if "import anthropic" in content:
                content = content.replace("import anthropic", "try:\n    import anthropic\nexcept ImportError:\n    anthropic = None")
            
            with open(services_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("[OK] Anthropic client 수정")
        else:
            print("[INFO] Anthropic client 이미 수정됨")
    else:
        print("[WARNING] services.py 파일 없음")

def fix_bulk_upload():
    """bulk-upload API CSRF 문제 수정"""
    print("\n4. BulkUploadView CSRF 처리")
    print("-" * 40)
    
    views_path = os.path.join(os.path.dirname(__file__), 'employees', 'views.py')
    
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # BulkUploadView에 csrf_exempt 추가
    if '@method_decorator(csrf_exempt' not in content:
        # method_decorator import 추가
        if 'from django.utils.decorators import method_decorator' not in content:
            content = content.replace(
                'from django.views.decorators.csrf import csrf_exempt',
                'from django.views.decorators.csrf import csrf_exempt\nfrom django.utils.decorators import method_decorator'
            )
        
        # BulkUploadView에 데코레이터 추가
        old_pattern = 'class BulkUploadView(View):'
        new_pattern = '@method_decorator(csrf_exempt, name="dispatch")\nclass BulkUploadView(View):'
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            print("[OK] BulkUploadView에 csrf_exempt 추가")
    else:
        print("[INFO] BulkUploadView CSRF 이미 처리됨")
    
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)

def create_env_example():
    """환경변수 예제 파일 생성"""
    print("\n5. 환경변수 예제 파일 생성")
    print("-" * 40)
    
    env_example = """.env.example
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,ehrv10-production.up.railway.app

# Database (Railway provides DATABASE_URL automatically)
# DATABASE_URL=postgresql://user:password@host:port/dbname

# AI APIs (Optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Proxy Settings (Optional)
# HTTP_PROXY=http://proxy.example.com:8080
# HTTPS_PROXY=http://proxy.example.com:8080
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_example)
    
    print("[OK] .env.example 생성")

def main():
    """메인 실행"""
    
    print("\n시작: Railway 경고 및 오류 통합 수정\n")
    
    # 1. OpenAI proxies 문제 수정
    fix_openai_proxies()
    
    # 2. TeamRecommendation 모델 생성
    fix_team_recommendation()
    
    # 3. Anthropic client 수정
    fix_anthropic_client()
    
    # 4. BulkUploadView CSRF 처리
    fix_bulk_upload()
    
    # 5. 환경변수 예제 생성
    create_env_example()
    
    print("\n" + "="*60)
    print("수정 완료!")
    print("="*60)
    print("\n다음 단계:")
    print("1. git add -A")
    print("2. git commit -m 'Fix all Railway warnings and errors'")
    print("3. git push")
    print("4. Railway 재배포 대기")
    print("\n주의사항:")
    print("- AI API 키가 없어도 기본 기능은 작동합니다")
    print("- TeamRecommendation 모델은 마이그레이션이 필요할 수 있습니다")

if __name__ == "__main__":
    main()