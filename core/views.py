from django.shortcuts import render

def under_construction(request):
    """개발 중인 페이지를 위한 임시 뷰"""
    return render(request, 'common/under_construction.html')