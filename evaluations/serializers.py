from rest_framework import serializers
from .models import (
    EvaluationPeriod, Task, Evaluation, EvaluationCriterion,
    Score, Feedback, Goal
)
from users.serializers import UserSerializer


class EvaluationPeriodSerializer(serializers.ModelSerializer):
    """Serializer for EvaluationPeriod model"""
    
    class Meta:
        model = EvaluationPeriod
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    assigned_by_detail = UserSerializer(source='assigned_by', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assigned_to', 'assigned_to_detail',
            'assigned_by', 'assigned_by_detail', 'status', 'priority',
            'start_date', 'due_date', 'completion_date', 'weight',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class EvaluationCriterionSerializer(serializers.ModelSerializer):
    """Serializer for EvaluationCriterion model"""
    
    class Meta:
        model = EvaluationCriterion
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ScoreSerializer(serializers.ModelSerializer):
    """Serializer for Score model"""
    criterion_detail = EvaluationCriterionSerializer(source='criterion', read_only=True)
    task_detail = TaskSerializer(source='task', read_only=True)
    
    class Meta:
        model = Score
        fields = [
            'id', 'evaluation', 'criterion', 'criterion_detail',
            'task', 'task_detail', 'score', 'comment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for Feedback model"""
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'evaluation', 'type', 'content', 'strengths',
            'improvements', 'recommendations', 'ai_prompt', 'ai_response',
            'created_by', 'created_by_detail', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'ai_response']


class GoalSerializer(serializers.ModelSerializer):
    """Serializer for Goal model"""
    employee_detail = UserSerializer(source='employee', read_only=True)
    
    class Meta:
        model = Goal
        fields = [
            'id', 'employee', 'employee_detail', 'evaluation',
            'title', 'description', 'target_date', 'status',
            'progress', 'achievement_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class EvaluationSerializer(serializers.ModelSerializer):
    """Serializer for Evaluation model"""
    employee_detail = UserSerializer(source='employee', read_only=True)
    evaluator_detail = UserSerializer(source='evaluator', read_only=True)
    period_detail = EvaluationPeriodSerializer(source='period', read_only=True)
    scores = ScoreSerializer(many=True, read_only=True)
    feedbacks = FeedbackSerializer(many=True, read_only=True)
    goals = GoalSerializer(many=True, read_only=True)
    
    class Meta:
        model = Evaluation
        fields = [
            'id', 'period', 'period_detail', 'employee', 'employee_detail',
            'evaluator', 'evaluator_detail', 'status', 'overall_score',
            'submitted_at', 'reviewed_at', 'scores', 'feedbacks', 'goals',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'overall_score']
        
    def create(self, validated_data):
        evaluation = super().create(validated_data)
        # Auto-create scores for all active criteria
        criteria = EvaluationCriterion.objects.filter(is_active=True)
        for criterion in criteria:
            Score.objects.get_or_create(
                evaluation=evaluation,
                criterion=criterion,
                defaults={'score': 0, 'comment': ''}
            )
        return evaluation


class EvaluationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing evaluations"""
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    evaluator_name = serializers.CharField(source='evaluator.get_full_name', read_only=True)
    period_name = serializers.CharField(source='period.name', read_only=True)
    
    class Meta:
        model = Evaluation
        fields = [
            'id', 'employee_name', 'evaluator_name', 'period_name',
            'status', 'overall_score', 'created_at'
        ]