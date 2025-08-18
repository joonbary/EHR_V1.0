from django.http import HttpResponse

def test_view(request):
    return HttpResponse("Job Profiles App is working!")