from django.shortcuts import render

def debug_navigation(request):
    """네비게이션 디버그 뷰"""
    context = {
        'user': None,  # Authentication removed
        'has_employee': False,  # Authentication removed
        'employee': None,  # Authentication removed
        'path': request.path,
        'method': request.method,
    }
    return render(request, 'evaluations/debug_navigation.html', context)