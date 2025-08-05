from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.core.paginator import Paginator
import json
import random

try:
    from employees.models import Employee
except ImportError:
    # Railway 환경에서 모델 임포트 문제 대비
    Employee = None

def msa_integration(request):
    """AIRISS MSA 통합 페이지"""
    employees_with_data = []
    
    if Employee:
        try:
            employees = Employee.objects.filter(employment_status="재직").values("id", "name", "department", "position")[:50]
            for emp in employees:
                emp_data = {
                    "id": emp["id"], "name": emp["name"], "department": emp["department"], "position": emp["position"],
                    "goalAchievement": random.randint(70, 100), "projectSuccess": random.randint(70, 100),
                    "customerSatisfaction": random.randint(70, 100), "attendance": random.randint(85, 100),
                }
                employees_with_data.append(emp_data)
        except Exception as e:
            # 오류 발생 시 샘플 데이터 사용
            employees_with_data = [
                {"id": 1, "name": "홍길동", "department": "개발팀", "position": "선임",
                 "goalAchievement": 85, "projectSuccess": 90, "customerSatisfaction": 88, "attendance": 95}
            ]
    else:
        # Employee 모델이 없을 때 샘플 데이터
        employees_with_data = [
            {"id": 1, "name": "홍길동", "department": "개발팀", "position": "선임",
             "goalAchievement": 85, "projectSuccess": 90, "customerSatisfaction": 88, "attendance": 95}
        ]
    
    context = {
        "employees": json.dumps(employees_with_data, ensure_ascii=False),
        "msa_url": "https://web-production-4066.up.railway.app",
        "page_title": "AIRISS AI 직원 분석",
    }
    return render(request, "airiss/msa_integration_simple.html", context)

def executive_dashboard(request):
    """경영진 대시보드"""
    # React 버전 사용 여부 확인
    use_react = request.GET.get('react', 'true').lower() == 'true'
    
    total_employees = 0
    dept_stats = []
    
    if Employee:
        try:
            total_employees = Employee.objects.filter(employment_status="재직").count()
            dept_stats = Employee.objects.filter(employment_status="재직").values("department").annotate(count=Count("id"), avg_score=Avg("id")).order_by("-count")
            dept_stats = list(dept_stats)
        except Exception as e:
            # 오류 발생 시 샘플 데이터
            total_employees = 173
            dept_stats = [
                {"department": "개발팀", "count": 45, "avg_score": 85},
                {"department": "영업팀", "count": 38, "avg_score": 82},
                {"department": "인사팀", "count": 25, "avg_score": 88}
            ]
    else:
        # Employee 모델이 없을 때 샘플 데이터
        total_employees = 173
        dept_stats = [
            {"department": "개발팀", "count": 45, "avg_score": 85},
            {"department": "영업팀", "count": 38, "avg_score": 82},
            {"department": "인사팀", "count": 25, "avg_score": 88}
        ]
    
    context = {
        "page_title": "경영진 대시보드",
        "total_employees": total_employees,
        "dept_stats": json.dumps(dept_stats, ensure_ascii=False),  # React를 위해 JSON으로 변환
        "ai_analysis_summary": {"high_performers": [], "risk_employees": [], "promotion_candidates": []},
        "grade_distribution": json.dumps({"S": 15, "A": 50, "B": 100, "C": 30, "D": 10}),
        "msa_url": "https://web-production-4066.up.railway.app",
        "last_updated": timezone.now()
    }
    
    # React 버전 사용 (원본 AIRISS UI 완전 통합)
    # Railway에서 템플릿 찾기 문제로 인해 simple 버전 사용
    return render(request, "airiss/executive_dashboard_simple.html", context)

def employee_analysis_all(request):
    """전직원 분석"""
    # React 버전 사용 여부
    use_react = request.GET.get('react', 'true').lower() == 'true'
    
    employees_with_analysis = []
    employees_page = None
    departments = []
    positions = []
    
    if Employee:
        try:
            employees_qs = Employee.objects.filter(employment_status="재직")
            paginator = Paginator(employees_qs, 20)
            employees_page = paginator.get_page(request.GET.get("page"))
            
            for emp in employees_page:
                score = random.randint(60, 95)
                employees_with_analysis.append({
                    "employee": emp, "analysis": None, "ai_score": score,
                    "ai_grade": "S" if score >= 90 else "A" if score >= 80 else "B" if score >= 70 else "C" if score >= 60 else "D"
                })
            
            departments = list(Employee.objects.filter(employment_status="재직").values_list("department", flat=True).distinct())
            positions = list(Employee.objects.filter(employment_status="재직").values_list("position", flat=True).distinct())
        except Exception as e:
            # 오류 발생 시 샘플 데이터
            pass
    
    if not employees_with_analysis:
        # 샘플 데이터
        class MockEmployee:
            def __init__(self, id, name, department, position, employee_number=None):
                self.id = id
                self.name = name
                self.department = department
                self.position = position
                self.employee_number = employee_number or f"EMP{id:03d}"
        
        sample_employees = [
            MockEmployee(1, "홍길동", "개발팀", "선임"),
            MockEmployee(2, "김철수", "영업팀", "과장"),
            MockEmployee(3, "이영희", "인사팀", "대리")
        ]
        
        for emp in sample_employees:
            score = random.randint(60, 95)
            employees_with_analysis.append({
                "employee": emp, "analysis": None, "ai_score": score,
                "ai_grade": "S" if score >= 90 else "A" if score >= 80 else "B" if score >= 70 else "C" if score >= 60 else "D"
            })
        
        departments = ["개발팀", "영업팀", "인사팀"]
        positions = ["선임", "과장", "대리"]
    
    # React용 JSON 변환
    employees_json = json.dumps([{
        "employee": {
            "id": item["employee"].id,
            "name": item["employee"].name,
            "department": item["employee"].department,
            "position": item["employee"].position,
            "employee_number": getattr(item["employee"], "employee_number", f"EMP{item['employee'].id:03d}")
        },
        "ai_score": item["ai_score"],
        "ai_grade": item["ai_grade"],
        "analysis": item["analysis"]
    } for item in employees_with_analysis], ensure_ascii=False)
    
    context = {
        "page_title": "전직원 분석", 
        "employees": employees_with_analysis,
        "employees_json": employees_json,  # React를 위한 JSON 데이터
        "employees_page": employees_page,
        "departments": json.dumps(departments, ensure_ascii=False) if use_react else departments,
        "positions": json.dumps(positions, ensure_ascii=False) if use_react else positions,
        "msa_url": "https://web-production-4066.up.railway.app"
    }
    
    # React 버전 사용 (원본 AIRISS UI 완전 통합)
    # Railway에서 템플릿 찾기 문제로 인해 simple 버전 사용
    return render(request, "airiss/employee_analysis_all_simple.html", context)

def employee_analysis_detail(request, employee_id):
    """개인별 분석결과 상세 조회"""
    employee = None
    
    if Employee:
        try:
            employee = get_object_or_404(Employee, id=employee_id)
        except Exception as e:
            # 오류 발생 시 샘플 데이터
            class MockEmployee:
                def __init__(self):
                    self.id = employee_id
                    self.name = "홍길동"
                    self.department = "개발팀"
                    self.position = "선임"
                    self.employee_number = "EMP001"
            employee = MockEmployee()
    else:
        # Employee 모델이 없을 때 샘플 데이터
        class MockEmployee:
            def __init__(self):
                self.id = employee_id
                self.name = "홍길동"
                self.department = "개발팀"
                self.position = "선임"
                self.employee_number = "EMP001"
        employee = MockEmployee()
    
    context = {
        "page_title": f"{employee.name}님의 분석 결과" if employee else "직원 분석 결과",
        "employee": employee,
        "msa_url": "https://web-production-4066.up.railway.app"
    }
    return render(request, "airiss/employee_analysis_detail_simple.html", context)


# 더미 뷰들 - base_modern.html의 URL 참조를 위해
def dashboard(request):
    """AIRISS 대시보드 - 준비중"""
    return render(request, "common/under_construction.html", {"page_title": "AIRISS 대시보드"})

def analytics(request):
    """HR 분석 - 준비중"""
    return render(request, "common/under_construction.html", {"page_title": "HR 분석"})

def predictions(request):
    """AI 예측 - 준비중"""
    return render(request, "common/under_construction.html", {"page_title": "AI 예측"})

def insights(request):
    """인사이트 - 준비중"""
    return render(request, "common/under_construction.html", {"page_title": "인사이트"})

def chatbot(request):
    """HR 챗봇 - 준비중"""
    return render(request, "common/under_construction.html", {"page_title": "HR 챗봇"})

def airiss_v4_portal(request):
    """AIRISS v4 포털 - 준비중"""
    return render(request, "common/under_construction.html", {"page_title": "AIRISS v4 포털"})
