"""
AIRISS 템플릿 오류 임시 수정
React 버전 대신 기존 Django 템플릿 사용
"""

# airiss/views.py의 executive_dashboard 함수에서
# use_react = request.GET.get('react', 'true').lower() == 'true'
# 를
# use_react = request.GET.get('react', 'false').lower() == 'true'
# 로 변경하여 기본값을 false로 설정

print("AIRISS 템플릿을 기존 Django 버전으로 사용하도록 설정합니다.")
print("React 버전을 사용하려면 URL에 ?react=true를 추가하세요.")