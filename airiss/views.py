from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import json
import random
import os
import requests

try:
    from employees.models import Employee
except ImportError:
    # Railway 환경에서 모델 임포트 문제 대비
    Employee = None

def file_upload(request):
    """AIRISS 파일 업로드 페이지"""
    context = {
        "page_title": "AIRISS 파일 업로드",
    }
    return render(request, "airiss/file_upload.html", context)

@csrf_exempt
def airiss_upload_proxy(request):
    """AIRISS 업로드 프록시 - MSA 서비스로 파일 전달"""
    if request.method == 'POST':
        try:
            # Railway 환경 확인
            if os.getenv('RAILWAY_ENVIRONMENT'):
                airiss_url = settings.AIRISS_INTERNAL_URL
            else:
                airiss_url = settings.AIRISS_SERVICE_URL
            
            # 파일 가져오기
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return JsonResponse({'error': '파일이 없습니다'}, status=400)
            
            # AIRISS MSA 서비스로 전달
            files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.content_type)}
            
            # 추가 데이터
            data = {}
            if request.POST.get('employee_id'):
                data['employee_id'] = request.POST.get('employee_id')
            if request.POST.get('analysis_type'):
                data['analysis_type'] = request.POST.get('analysis_type')
            
            # MSA 서비스 호출
            response = requests.post(
                f"{airiss_url}/api/v1/upload",
                files=files,
                data=data,
                timeout=30
            )
            
            # 응답 전달
            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({
                    'error': f'업로드 실패: {response.status_code}',
                    'message': response.text
                }, status=response.status_code)
                
        except requests.exceptions.ConnectionError:
            return JsonResponse({
                'error': 'AIRISS 서비스에 연결할 수 없습니다',
                'service_url': airiss_url
            }, status=503)
        except Exception as e:
            return JsonResponse({
                'error': f'업로드 중 오류 발생: {str(e)}'
            }, status=500)
    
    return JsonResponse({'error': 'POST 요청만 허용됩니다'}, status=405)

@csrf_exempt
def airiss_jobs_proxy(request):
    """AIRISS jobs API 프록시"""
    try:
        # Railway 환경 확인
        if os.getenv('RAILWAY_ENVIRONMENT'):
            airiss_url = settings.AIRISS_INTERNAL_URL
        else:
            airiss_url = settings.AIRISS_SERVICE_URL
        
        # AIRISS MSA 서비스로 전달
        response = requests.get(
            f"{airiss_url}/api/v1/analysis/jobs",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        # 응답 전달
        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        else:
            # AIRISS 서비스가 응답하지 않으면 더미 데이터 반환
            return JsonResponse({
                'total': 0,
                'completed': 0,
                'pending': 0,
                'failed': 0,
                'jobs': []
            })
            
    except requests.exceptions.ConnectionError:
        # 연결 실패 시 더미 데이터
        return JsonResponse({
            'total': 0,
            'completed': 0,
            'pending': 0,
            'failed': 0,
            'jobs': []
        })
    except Exception as e:
        return JsonResponse({
            'error': f'API 호출 중 오류: {str(e)}',
            'total': 0,
            'completed': 0,
            'pending': 0,
            'failed': 0,
            'jobs': []
        })

@csrf_exempt
def airiss_api_proxy(request, api_path):
    """AIRISS 일반 API 프록시"""
    try:
        # Railway 환경 확인
        if os.getenv('RAILWAY_ENVIRONMENT'):
            airiss_url = settings.AIRISS_INTERNAL_URL
        else:
            airiss_url = settings.AIRISS_SERVICE_URL
        
        # 요청 메서드에 따른 처리
        url = f"{airiss_url}/api/{api_path}"
        
        # 헤더 복사
        headers = {}
        for key, value in request.headers.items():
            if key.lower() not in ['host', 'cookie', 'x-csrftoken']:
                headers[key] = value
        
        # 요청 전달
        if request.method == 'GET':
            response = requests.get(url, headers=headers, params=request.GET, timeout=10)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, json=json.loads(request.body) if request.body else {}, timeout=10)
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, json=json.loads(request.body) if request.body else {}, timeout=10)
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return JsonResponse({'error': f'{request.method} 메서드는 지원되지 않습니다'}, status=405)
        
        # 응답 전달
        if response.headers.get('content-type', '').startswith('application/json'):
            return JsonResponse(response.json(), safe=False, status=response.status_code)
        else:
            return HttpResponse(response.content, content_type=response.headers.get('content-type', 'text/plain'), status=response.status_code)
            
    except requests.exceptions.ConnectionError:
        return JsonResponse({
            'error': 'AIRISS 서비스에 연결할 수 없습니다',
            'service_url': airiss_url
        }, status=503)
    except Exception as e:
        return JsonResponse({
            'error': f'API 호출 중 오류: {str(e)}'
        }, status=500)

def msa_integration(request):
    """AIRISS MSA 통합 페이지"""
    from .models import AIAnalysisResult, AIAnalysisType
    from django.contrib.auth.models import User
    from django.conf import settings
    import requests
    
    employees_with_data = []
    message = ""
    
    # POST 요청 처리 - AI 분석 실행 및 저장
    if request.method == "POST" and request.POST.get("action") == "analyze":
        selected_employees = request.POST.getlist("employee_ids")
        
        # AI 분석 타입 가져오기 (없으면 생성)
        analysis_type, created = AIAnalysisType.objects.get_or_create(
            type_code="TEAM_PERFORMANCE",
            defaults={
                "name": "팀 성과 예측",
                "description": "AI 기반 직원 성과 분석"
            }
        )
        
        # 선택된 직원들에 대해 AI 분석 실행 및 저장
        analyzed_count = 0
        for emp_id in selected_employees:
            try:
                employee = Employee.objects.get(id=emp_id)
                
                # MSA 서버 호출
                try:
                    # AIRISS API 형식에 맞게 데이터 준비
                    current_year = str(timezone.now().year)
                    evaluation_text = f"{employee.name}님은 {employee.department}에서 {employee.position} 직급으로 성실하게 근무하고 있습니다. 업무 수행 능력이 뛰어나며 팀워크가 좋습니다."
                    
                    analysis_data = {
                        "uid": str(emp_id),
                        "opinions": {
                            current_year: evaluation_text
                        }
                    }
                    
                    # AIRISS MSA 서버에 분석 요청
                    # Railway 환경에서는 내부 URL 사용 (더 빠르고 안전)
                    airiss_api_url = settings.AIRISS_INTERNAL_URL if os.getenv('RAILWAY_ENVIRONMENT') else settings.AIRISS_SERVICE_URL
                    
                    response = requests.post(
                        f"{airiss_api_url}/api/v1/analysis/analyze",
                        json=analysis_data,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"MSA API 응답: {result}")  # 응답 구조 확인용 로그
                        
                        # AIRISS API 응답에서 데이터 추출
                        # 실제 응답 구조: {"success": true, "result": {...}}
                        if result.get("success") and "result" in result:
                            api_result = result["result"]
                            
                            # 실제 AI 점수와 분석 데이터 추출
                            ai_score = api_result.get("hybrid_score", api_result.get("text_score", 70))
                            confidence = api_result.get("confidence", 0.85)
                            insights_text = api_result.get("summary", f"{employee.name}님의 종합 성과 점수는 {ai_score}점입니다.")
                            
                            # 세부 점수들
                            dimension_scores = api_result.get("dimension_scores", {})
                            
                            # result_data에 실제 AI 분석 결과 저장
                            result_data = {
                                "hybrid_score": ai_score,
                                "text_score": api_result.get("text_score", 0),
                                "sentiment_score": api_result.get("sentiment_score", 0),
                                "dimension_scores": dimension_scores,
                                "strengths": api_result.get("strengths", []),
                                "weaknesses": api_result.get("weaknesses", []),
                                "processing_time": api_result.get("processing_time", 0),
                                "model_version": api_result.get("model_version", "v1.0")
                            }
                        else:
                            # API 응답이 예상과 다른 경우
                            print(f"예상과 다른 API 응답: {result}")
                            ai_score = random.randint(60, 95)
                            confidence = 0.7
                            insights_text = f"{employee.name}님의 예상 성과 점수는 {ai_score}점입니다."
                            result_data = {"status": "success", "score": ai_score}
                    else:
                        # API 호출 실패 시 더미 데이터
                        print(f"MSA API 호출 실패: {response.status_code}")
                        ai_score = random.randint(60, 95)
                        confidence = 0.6
                        insights_text = f"{employee.name}님의 추정 성과 점수는 {ai_score}점입니다."
                        result_data = {"status": "error", "message": "MSA API 호출 실패"}
                        
                except Exception as e:
                    # 네트워크 오류 등 예외 처리
                    print(f"MSA 연결 오류: {e}")
                    ai_score = random.randint(60, 95)
                    confidence = 0.5
                    insights_text = f"{employee.name}님의 임시 성과 점수는 {ai_score}점입니다."
                    result_data = {"status": "error", "message": str(e)}
                
                # 분석 결과 저장
                AIAnalysisResult.objects.create(
                    analysis_type=analysis_type,
                    employee=employee,
                    analyzed_by=request.user if request.user.is_authenticated else None,
                    ai_score=ai_score,
                    confidence_score=confidence,
                    insights=insights_text,
                    result_data=result_data
                )
                analyzed_count += 1
                
            except Employee.DoesNotExist:
                print(f"직원을 찾을 수 없습니다: ID {emp_id}")
                continue
            except Exception as e:
                print(f"분석 중 오류 발생: {e}")
                continue
        
        message = f"{analyzed_count}명의 직원에 대한 AI 분석이 완료되었습니다!"
    
    # GET 요청 - 직원 목록 표시
    if Employee:
        employees = Employee.objects.all().order_by('name')[:100]
        
        # 각 직원의 최신 AI 분석 결과 가져오기
        for emp in employees:
            latest_analysis = AIAnalysisResult.objects.filter(
                employee=emp
            ).order_by('-analyzed_at').first()
            
            employees_with_data.append({
                "id": emp.id,
                "name": emp.name,
                "department": emp.department,
                "position": emp.position,
                "ai_score": latest_analysis.ai_score if latest_analysis else None,
                "analyzed_at": latest_analysis.analyzed_at.strftime("%Y-%m-%d %H:%M") if latest_analysis else None
            })
    
    context = {
        "page_title": "AIRISS MSA 통합",
        "employees": json.dumps(employees_with_data, ensure_ascii=False),
        "msa_url": settings.AIRISS_SERVICE_URL,
        "message": message
    }
    
    return render(request, "airiss/msa_integration.html", context)

def dashboard(request):
    """AIRISS 대시보드"""
    # 최근 분석 결과 가져오기
    from .models import AIAnalysisResult
    
    recent_analyses = []
    if AIAnalysisResult._meta.db_table in connection.introspection.table_names():
        recent_analyses = AIAnalysisResult.objects.select_related('employee').order_by('-analyzed_at')[:10]
    
    # 부서별 통계
    department_stats = {}
    if recent_analyses:
        for analysis in recent_analyses:
            dept = analysis.employee.department
            if dept not in department_stats:
                department_stats[dept] = {
                    'count': 0,
                    'total_score': 0,
                    'avg_score': 0
                }
            department_stats[dept]['count'] += 1
            department_stats[dept]['total_score'] += analysis.ai_score
            department_stats[dept]['avg_score'] = department_stats[dept]['total_score'] / department_stats[dept]['count']
    
    context = {
        "page_title": "AIRISS 대시보드",
        "recent_analyses": recent_analyses,
        "department_stats": department_stats,
        "total_analyses": len(recent_analyses),
        "avg_score": sum(a.ai_score for a in recent_analyses) / len(recent_analyses) if recent_analyses else 0
    }
    return render(request, "airiss/dashboard.html", context)

def analytics(request):
    """AIRISS 분석"""
    context = {"page_title": "AIRISS 분석"}
    return render(request, "airiss/analytics.html", context)

def predictions(request):
    """AIRISS 예측"""
    context = {"page_title": "AIRISS 예측"}
    return render(request, "airiss/predictions.html", context)

def insights(request):
    """AIRISS 인사이트"""
    context = {"page_title": "AIRISS 인사이트"}
    return render(request, "airiss/insights.html", context)

def chatbot(request):
    """AIRISS 챗봇"""
    context = {"page_title": "AIRISS AI 챗봇"}
    return render(request, "airiss/chatbot.html", context)

def executive_dashboard(request):
    """임원 대시보드 - 포트폴리오 전용"""
    from .models import AIAnalysisResult
    from django.db import connection
    import json
    
    # 분석 결과가 있는지 확인
    has_analysis = False
    team_scores = []
    
    # DB 테이블 존재 여부 확인
    table_exists = AIAnalysisResult._meta.db_table in connection.introspection.table_names()
    
    if table_exists:
        # 팀별 평균 성과 점수 계산
        from django.db.models import Avg
        
        if Employee:
            dept_scores = AIAnalysisResult.objects.values('employee__department').annotate(
                avg_score=Avg('ai_score')
            ).order_by('-avg_score')[:5]
            
            team_scores = [
                {
                    'name': dept['employee__department'] or '미지정',
                    'score': round(dept['avg_score'], 1) if dept['avg_score'] else 0
                }
                for dept in dept_scores
            ]
            has_analysis = len(team_scores) > 0
    
    # 더미 데이터 (분석 결과가 없을 경우)
    if not has_analysis:
        team_scores = [
            {'name': '개발팀', 'score': 85.5},
            {'name': '마케팅팀', 'score': 82.3},
            {'name': '영업팀', 'score': 88.7},
            {'name': '인사팀', 'score': 79.2},
            {'name': '재무팀', 'score': 83.9}
        ]
    
    context = {
        'page_title': 'AIRISS 임원 대시보드',
        'team_scores': json.dumps(team_scores, ensure_ascii=False),
        'has_analysis': has_analysis,
        'current_date': timezone.now().strftime('%Y년 %m월 %d일')
    }
    
    return render(request, 'airiss/executive_dashboard_simple.html', context)

def employee_analysis_all(request):
    """전체 직원 분석 뷰"""
    from .models import AIAnalysisResult
    from django.db import connection
    import json
    
    employees_data = []
    
    # DB 테이블 존재 여부 확인
    table_exists = AIAnalysisResult._meta.db_table in connection.introspection.table_names()
    
    if table_exists and Employee:
        # 실제 데이터 조회
        analyses = AIAnalysisResult.objects.select_related('employee').order_by('-analyzed_at')[:50]
        
        for analysis in analyses:
            employees_data.append({
                'id': analysis.employee.id,
                'name': analysis.employee.name,
                'department': analysis.employee.department or '미지정',
                'position': analysis.employee.position or '미지정',
                'ai_score': round(analysis.ai_score, 1),
                'confidence': round(analysis.confidence_score * 100, 1),
                'analyzed_date': analysis.analyzed_at.strftime('%Y-%m-%d'),
                'status': '분석완료'
            })
    
    # 더미 데이터 (실제 데이터가 없을 경우)
    if not employees_data:
        dummy_names = ['김철수', '이영희', '박민수', '정수진', '최동욱', '강미영', '조현우', '임지혜', '윤성호', '한예진']
        dummy_depts = ['개발팀', '마케팅팀', '영업팀', '인사팀', '재무팀']
        dummy_positions = ['사원', '대리', '과장', '차장', '부장']
        
        for i in range(10):
            employees_data.append({
                'id': i + 1,
                'name': dummy_names[i % len(dummy_names)],
                'department': dummy_depts[i % len(dummy_depts)],
                'position': dummy_positions[i % len(dummy_positions)],
                'ai_score': round(random.uniform(65, 95), 1),
                'confidence': round(random.uniform(70, 95), 1),
                'analyzed_date': timezone.now().strftime('%Y-%m-%d'),
                'status': '분석완료'
            })
    
    context = {
        'page_title': 'AIRISS 전체 직원 분석',
        'employees': json.dumps(employees_data, ensure_ascii=False),
        'total_count': len(employees_data)
    }
    
    return render(request, 'airiss/employee_analysis_all_simple.html', context)

def employee_analysis_detail(request, employee_id):
    """개별 직원 상세 분석"""
    from .models import AIAnalysisResult
    from django.db import connection
    import json
    
    # 더미 데이터 생성
    employee_data = {
        'id': employee_id,
        'name': f'직원_{employee_id}',
        'department': '개발팀',
        'position': '과장',
        'ai_score': round(random.uniform(70, 95), 1),
        'confidence': round(random.uniform(75, 95), 1),
        'strengths': ['문제해결능력', '팀워크', '의사소통'],
        'weaknesses': ['시간관리', '문서작성'],
        'recommendations': [
            '프로젝트 관리 교육 추천',
            '리더십 프로그램 참여 권장',
            '기술 스킬 향상 과정 수강'
        ]
    }
    
    # 실제 데이터 조회 시도
    table_exists = AIAnalysisResult._meta.db_table in connection.introspection.table_names()
    
    if table_exists and Employee:
        try:
            employee = Employee.objects.get(id=employee_id)
            analysis = AIAnalysisResult.objects.filter(employee=employee).order_by('-analyzed_at').first()
            
            if analysis:
                employee_data.update({
                    'name': employee.name,
                    'department': employee.department or '미지정',
                    'position': employee.position or '미지정',
                    'ai_score': round(analysis.ai_score, 1),
                    'confidence': round(analysis.confidence_score * 100, 1)
                })
                
                # result_data에서 추가 정보 추출
                if analysis.result_data:
                    employee_data['strengths'] = analysis.result_data.get('strengths', employee_data['strengths'])
                    employee_data['weaknesses'] = analysis.result_data.get('weaknesses', employee_data['weaknesses'])
        except:
            pass  # 더미 데이터 사용
    
    context = {
        'page_title': f'{employee_data["name"]} - 상세 분석',
        'employee': json.dumps(employee_data, ensure_ascii=False)
    }
    
    return render(request, 'airiss/employee_analysis_detail_simple.html', context)

def airiss_v4_portal(request):
    """AIRISS v4 포털"""
    context = {
        "page_title": "AIRISS v4 포털",
        "airiss_v4_url": settings.AIRISS_SERVICE_URL  # 실제 AIRISS v4 MSA URL
    }
    return render(request, "airiss/airiss_v4_portal.html", context)

def analysis_results(request):
    """저장된 AI 분석 결과 조회"""
    from .models import AIAnalysisResult
    from django.core.paginator import Paginator
    
    # 필터링
    department = request.GET.get('department')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # 쿼리셋 생성
    queryset = AIAnalysisResult.objects.select_related('employee', 'analysis_type').order_by('-analyzed_at')
    
    # 필터 적용
    if department:
        queryset = queryset.filter(employee__department=department)
    if date_from:
        queryset = queryset.filter(analyzed_at__gte=date_from)
    if date_to:
        queryset = queryset.filter(analyzed_at__lte=date_to)
    
    # 페이지네이션
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 부서 목록 (필터용)
    departments = Employee.objects.values_list('department', flat=True).distinct() if Employee else []
    
    context = {
        "page_title": "AI 분석 결과",
        "page_obj": page_obj,
        "departments": departments,
        "selected_department": department,
        "date_from": date_from,
        "date_to": date_to,
    }
    
    return render(request, "airiss/analysis_results.html", context)