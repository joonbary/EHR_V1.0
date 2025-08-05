from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def debug_navigation(request):
    """네비게이션 디버그 뷰"""
    context = {
        'user': request.user,
        'has_employee': hasattr(request.user, 'employee'),
        'employee': getattr(request.user, 'employee', None),
        'path': request.path,
        'method': request.method,
    }
    return render(request, 'evaluations/debug_navigation.html', context)