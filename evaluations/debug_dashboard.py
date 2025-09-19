"""
Debug view for evaluation dashboard
"""
from django.http import HttpResponse
from django.db import connection
from .models import ComprehensiveEvaluation, ContributionEvaluation
import traceback

def debug_dashboard(request):
    """Debug evaluation dashboard issues"""
    output = []
    output.append("=" * 60)
    output.append("Evaluation Dashboard Debug")
    output.append("=" * 60)
    
    # 1. Check ComprehensiveEvaluation fields
    output.append("\n1. ComprehensiveEvaluation Model Fields:")
    try:
        fields = [f.name for f in ComprehensiveEvaluation._meta.fields]
        output.append(f"Fields: {', '.join(fields)}")
    except Exception as e:
        output.append(f"Error getting fields: {str(e)}")
    
    # 2. Test simple query
    output.append("\n2. Test Simple Query:")
    try:
        count = ComprehensiveEvaluation.objects.count()
        output.append(f"Total ComprehensiveEvaluation records: {count}")
    except Exception as e:
        output.append(f"Error counting records: {str(e)}")
        output.append(f"Traceback: {traceback.format_exc()}")
    
    # 3. Test grade field query
    output.append("\n3. Test Grade Field Query:")
    try:
        from django.db.models import Count
        
        # Try final_grade
        try:
            grade_counts = ComprehensiveEvaluation.objects.values('final_grade').annotate(count=Count('id'))
            output.append(f"final_grade query successful: {list(grade_counts)[:3]}")
        except Exception as e:
            output.append(f"final_grade query failed: {str(e)}")
        
        # Try manager_grade
        try:
            grade_counts = ComprehensiveEvaluation.objects.values('manager_grade').annotate(count=Count('id'))
            output.append(f"manager_grade query successful: {list(grade_counts)[:3]}")
        except Exception as e:
            output.append(f"manager_grade query failed: {str(e)}")
            
    except Exception as e:
        output.append(f"Grade query error: {str(e)}")
    
    # 4. Test status field
    output.append("\n4. Test Status Field:")
    try:
        status_query = ComprehensiveEvaluation.objects.filter(status='COMPLETED')
        output.append(f"Status query successful, count: {status_query.count()}")
    except Exception as e:
        output.append(f"Status query failed: {str(e)}")
    
    # 5. Check ContributionEvaluation
    output.append("\n5. ContributionEvaluation Check:")
    try:
        fields = [f.name for f in ContributionEvaluation._meta.fields]
        output.append(f"Fields: {', '.join(fields)}")
        count = ContributionEvaluation.objects.count()
        output.append(f"Total records: {count}")
    except Exception as e:
        output.append(f"Error: {str(e)}")
    
    # 6. Check Database tables
    output.append("\n6. Database Tables:")
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE 'evaluations_%'
                ORDER BY name
            """)
            tables = cursor.fetchall()
            for table in tables:
                output.append(f"  - {table[0]}")
    except Exception as e:
        output.append(f"Error checking tables: {str(e)}")
    
    # 7. Test the actual view logic
    output.append("\n7. Test View Logic:")
    try:
        from .models import EvaluationPeriod
        from employees.models import Employee
        
        # Check active period
        active_period = EvaluationPeriod.objects.filter(is_active=True).first()
        output.append(f"Active period: {active_period}")
        
        # Check employees
        emp_count = Employee.objects.filter(employment_status='재직').count()
        output.append(f"Active employees: {emp_count}")
        
        if active_period:
            # Test the problematic query
            try:
                top_evaluations = ComprehensiveEvaluation.objects.filter(
                    evaluation_period=active_period,
                    status='COMPLETED'
                ).select_related('employee').order_by('-total_score')[:5]
                output.append(f"Top evaluations query successful: {top_evaluations.count()} records")
            except Exception as e:
                output.append(f"Top evaluations query failed: {str(e)}")
                output.append(f"Traceback: {traceback.format_exc()}")
                
    except Exception as e:
        output.append(f"View logic test error: {str(e)}")
        output.append(f"Traceback: {traceback.format_exc()}")
    
    return HttpResponse('\n'.join(output), content_type='text/plain')