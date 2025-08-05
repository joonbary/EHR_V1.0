from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.core.paginator import Paginator
import json
import random

from employees.models import Employee

def msa_integration(request):
    """AIRISS MSA 통합 페이지"""
    employees = Employee.objects.filter(employment_status="재직").values("id", "name", "department", "position")[:50]
    
    employees_with_data = []
    for emp in employees:
        emp_data = {
            "id": emp["id"], "name": emp["name"], "department": emp["department"], "position": emp["position"],
            "goalAchievement": random.randint(70, 100), "projectSuccess": random.randint(70, 100),
            "customerSatisfaction": random.randint(70, 100), "attendance": random.randint(85, 100),
        }
        employees_with_data.append(emp_data)
    
    context = {
        "employees": json.dumps(employees_with_data, ensure_ascii=False),
        "msa_url": "https://web-production-4066.up.railway.app",
        "page_title": "AIRISS AI 직원 분석",
    }
    return render(request, "airiss/msa_integration.html", context)

def executive_dashboard(request):
    """경영진 대시보드"""
    total_employees = Employee.objects.filter(employment_status="재직").count()
    dept_stats = Employee.objects.filter(employment_status="재직").values("department").annotate(count=Count("id"), avg_score=Avg("id")).order_by("-count")
    
    context = {
        "page_title": "경영진 대시보드",
        "total_employees": total_employees,
        "dept_stats": list(dept_stats),
        "ai_analysis_summary": {"high_performers": [], "risk_employees": [], "promotion_candidates": []},
        "grade_distribution": json.dumps({"S": 15, "A": 50, "B": 100, "C": 30, "D": 10}),
        "msa_url": "https://web-production-4066.up.railway.app",
        "last_updated": timezone.now()
    }
    return render(request, "airiss/executive_dashboard.html", context)

def employee_analysis_all(request):
    """전직원 분석"""
    employees_qs = Employee.objects.filter(employment_status="재직")
    paginator = Paginator(employees_qs, 20)
    employees_page = paginator.get_page(request.GET.get("page"))
    
    employees_with_analysis = []
    for emp in employees_page:
        score = random.randint(60, 95)
        employees_with_analysis.append({
            "employee": emp, "analysis": None, "ai_score": score,
            "ai_grade": "S" if score >= 90 else "A" if score >= 80 else "B" if score >= 70 else "C" if score >= 60 else "D"
        })
    
    context = {
        "page_title": "전직원 분석", "employees": employees_with_analysis, "employees_page": employees_page,
        "departments": list(Employee.objects.filter(employment_status="재직").values_list("department", flat=True).distinct()),
        "positions": list(Employee.objects.filter(employment_status="재직").values_list("position", flat=True).distinct()),
        "msa_url": "https://web-production-4066.up.railway.app"
    }
    return render(request, "airiss/employee_analysis_all.html", context)

def employee_analysis_detail(request, employee_id):
    """개인별 분석결과 상세 조회"""
    employee = get_object_or_404(Employee, id=employee_id)
    context = {
        "page_title": f"{employee.name}님의 분석 결과",
        "employee": employee,
        "msa_url": "https://web-production-4066.up.railway.app"
    }
    return render(request, "airiss/employee_analysis_detail.html", context)

# 더미 뷰들 - base_modern.html 호환성을 위해
def dashboard(request):
    """AIRISS 대시보드 (더미)"""
    return render(request, "airiss/dashboard.html", {"page_title": "AIRISS 대시보드"})

def analytics(request):
    """분석 페이지 (더미)"""
    return render(request, "airiss/analytics.html", {"page_title": "분석"})

def predictions(request):
    """예측 페이지 (더미)"""
    return render(request, "airiss/predictions.html", {"page_title": "예측"})

def insights(request):
    """인사이트 페이지 (더미)"""
    return render(request, "airiss/insights.html", {"page_title": "인사이트"})

def chatbot(request):
    """챗봇 페이지 (더미)"""
    return render(request, "airiss/chatbot.html", {"page_title": "AI 챗봇"})

def airiss_v4_portal(request):
    """AIRISS V4 포털 (더미)"""
    return render(request, "airiss/airiss_v4_portal.html", {"page_title": "AIRISS V4 포털"})
