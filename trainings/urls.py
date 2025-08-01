"""
교육 관련 URL 패턴
"""

from django.urls import path
from .training_api import (
    MyGrowthTrainingRecommendationsAPI,
    TrainingEnrollmentAPI,
    MyTrainingHistoryAPI,
    TrainingCourseDetailAPI
)

app_name = 'trainings'

urlpatterns = [
    # API 엔드포인트
    path('api/my-growth-training-recommendations/', 
         MyGrowthTrainingRecommendationsAPI.as_view(), 
         name='my_growth_training_recommendations'),
    
    path('api/training-enrollment/', 
         TrainingEnrollmentAPI.as_view(), 
         name='training_enrollment'),
    
    path('api/my-training-history/', 
         MyTrainingHistoryAPI.as_view(), 
         name='my_training_history'),
    
    path('api/training-course/<uuid:course_id>/', 
         TrainingCourseDetailAPI.as_view(), 
         name='training_course_detail'),
]