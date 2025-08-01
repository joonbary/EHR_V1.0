# 마이그레이션 가이드

## 1. 기존 로그인 기능 제거

### 1.1 URL 패턴 수정
```python
# ehr_system/urls.py

from django.contrib import admin
from django.urls import path, include
from job_profiles.views import JobTreeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', JobTreeView.as_view(), name='home'),  # 루트를 직무 트리맵으로
    path('', include('job_profiles.urls')),
    
    # 로그인 관련 URL 제거
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
```

### 1.2 뷰에서 @login_required 데코레이터 제거
```python
# 모든 뷰에서 @login_required 제거
# from django.contrib.auth.decorators import login_required  # 제거

def some_view(request):  # @login_required 제거
    # 뷰 로직
    pass
```

### 1.3 템플릿에서 로그인 체크 제거
```html
<!-- 기존 -->
{% if user.is_authenticated %}
    <!-- 로그인한 사용자 -->
{% else %}
    <!-- 로그인하지 않은 사용자 -->
{% endif %}

<!-- 변경 후 -->
<!-- 모든 사용자가 접근 가능하므로 조건문 제거 -->
```

## 2. 데이터베이스 마이그레이션

```bash
# 새로운 마이그레이션 생성
python manage.py makemigrations

# 마이그레이션 적용
python manage.py migrate

# 정적 파일 수집
python manage.py collectstatic
```

## 3. 서버 재시작

```bash
# 개발 서버 재시작
python manage.py runserver
```

## 4. 확인사항

1. 루트 URL(/)이 직무 트리맵으로 연결되는지 확인
2. 모든 페이지가 로그인 없이 접근 가능한지 확인
3. 직무 상세 모달이 정상 작동하는지 확인
4. 편집/삭제 기능이 정상 작동하는지 확인
