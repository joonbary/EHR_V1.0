from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('under-construction/', views.under_construction, name='under_construction'),
]