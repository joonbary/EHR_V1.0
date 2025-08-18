from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EvaluationPeriodViewSet, TaskViewSet, EvaluationViewSet,
    EvaluationCriterionViewSet, ScoreViewSet, FeedbackViewSet, GoalViewSet
)

router = DefaultRouter()
router.register(r'periods', EvaluationPeriodViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'evaluations', EvaluationViewSet)
router.register(r'criteria', EvaluationCriterionViewSet)
router.register(r'scores', ScoreViewSet)
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'goals', GoalViewSet)

app_name = 'evaluations'

urlpatterns = [
    path('', include(router.urls)),
]