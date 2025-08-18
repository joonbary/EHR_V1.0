from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Avg
from django.utils import timezone
from .models import (
    EvaluationPeriod, Task, Evaluation, EvaluationCriterion,
    Score, Feedback, Goal
)
from .serializers import (
    EvaluationPeriodSerializer, TaskSerializer, EvaluationSerializer,
    EvaluationCriterionSerializer, ScoreSerializer, FeedbackSerializer,
    GoalSerializer, EvaluationListSerializer
)
from .ai_service import generate_ai_feedback


class EvaluationPeriodViewSet(viewsets.ModelViewSet):
    """ViewSet for EvaluationPeriod CRUD operations"""
    queryset = EvaluationPeriod.objects.all()
    serializer_class = EvaluationPeriodSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active evaluation period"""
        active_period = self.queryset.filter(is_active=True).first()
        if active_period:
            serializer = self.get_serializer(active_period)
            return Response(serializer.data)
        return Response({'detail': 'No active period found'}, status=status.HTTP_404_NOT_FOUND)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task CRUD operations"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Filter based on user role
        if user.role == 'employee':
            queryset = queryset.filter(assigned_to=user)
        elif user.role == 'evaluator':
            queryset = queryset.filter(
                Q(assigned_to__in=user.evaluations_given.values_list('employee', flat=True)) |
                Q(assigned_by=user)
            )
        
        # Apply filters from query params
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        priority_filter = self.request.query_params.get('priority', None)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark task as completed"""
        task = self.get_object()
        task.status = 'completed'
        task.completion_date = timezone.now().date()
        task.save()
        return Response({'status': 'task completed'})


class EvaluationViewSet(viewsets.ModelViewSet):
    """ViewSet for Evaluation CRUD operations"""
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EvaluationListSerializer
        return EvaluationSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Filter based on user role
        if user.role == 'employee':
            queryset = queryset.filter(employee=user)
        elif user.role == 'evaluator':
            queryset = queryset.filter(Q(evaluator=user) | Q(employee=user))
        
        # Apply filters
        period_id = self.request.query_params.get('period', None)
        if period_id:
            queryset = queryset.filter(period_id=period_id)
            
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit evaluation for review"""
        evaluation = self.get_object()
        if evaluation.status != 'draft':
            return Response(
                {'detail': 'Only draft evaluations can be submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        evaluation.status = 'submitted'
        evaluation.submitted_at = timezone.now()
        evaluation.calculate_overall_score()
        evaluation.save()
        
        # Create notification
        from notifications.models import Notification
        Notification.create_notification(
            recipient=evaluation.employee,
            type='evaluation_submitted',
            title='Evaluation Submitted',
            message=f'Your evaluation for {evaluation.period.name} has been submitted by {evaluation.evaluator.get_full_name()}',
            sender=evaluation.evaluator
        )
        
        return Response({'status': 'evaluation submitted'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve evaluation"""
        evaluation = self.get_object()
        if evaluation.status != 'submitted':
            return Response(
                {'detail': 'Only submitted evaluations can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        evaluation.status = 'approved'
        evaluation.reviewed_at = timezone.now()
        evaluation.save()
        
        # Create notification
        from notifications.models import Notification
        Notification.create_notification(
            recipient=evaluation.employee,
            type='evaluation_approved',
            title='Evaluation Approved',
            message=f'Your evaluation for {evaluation.period.name} has been approved',
            sender=request.user
        )
        
        return Response({'status': 'evaluation approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject evaluation"""
        evaluation = self.get_object()
        if evaluation.status != 'submitted':
            return Response(
                {'detail': 'Only submitted evaluations can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        evaluation.status = 'rejected'
        evaluation.reviewed_at = timezone.now()
        evaluation.save()
        
        # Create notification
        from notifications.models import Notification
        Notification.create_notification(
            recipient=evaluation.evaluator,
            type='evaluation_rejected',
            title='Evaluation Rejected',
            message=f'The evaluation for {evaluation.employee.get_full_name()} has been rejected and needs revision',
            sender=request.user
        )
        
        return Response({'status': 'evaluation rejected'})
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get evaluation analytics"""
        evaluation = self.get_object()
        scores = evaluation.scores.all()
        
        # Calculate category averages
        category_scores = {}
        for score in scores:
            category = score.criterion.category
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(score.score)
        
        category_averages = {
            category: sum(scores) / len(scores) if scores else 0
            for category, scores in category_scores.items()
        }
        
        # Get task completion rate
        tasks = Task.objects.filter(assigned_to=evaluation.employee)
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='completed').count()
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return Response({
            'overall_score': evaluation.overall_score,
            'category_averages': category_averages,
            'task_completion_rate': completion_rate,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks
        })


class EvaluationCriterionViewSet(viewsets.ModelViewSet):
    """ViewSet for EvaluationCriterion CRUD operations"""
    queryset = EvaluationCriterion.objects.filter(is_active=True)
    serializer_class = EvaluationCriterionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class ScoreViewSet(viewsets.ModelViewSet):
    """ViewSet for Score CRUD operations"""
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        evaluation_id = self.request.query_params.get('evaluation', None)
        if evaluation_id:
            queryset = queryset.filter(evaluation_id=evaluation_id)
        return queryset
    
    def update(self, request, *args, **kwargs):
        """Update score and recalculate overall score"""
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            score = self.get_object()
            score.evaluation.calculate_overall_score()
        return response


class FeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for Feedback CRUD operations"""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        evaluation_id = self.request.query_params.get('evaluation', None)
        if evaluation_id:
            queryset = queryset.filter(evaluation_id=evaluation_id)
        return queryset
    
    @action(detail=False, methods=['post'])
    def generate_ai(self, request):
        """Generate AI feedback for evaluation"""
        evaluation_id = request.data.get('evaluation_id')
        if not evaluation_id:
            return Response(
                {'detail': 'evaluation_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            evaluation = Evaluation.objects.get(id=evaluation_id)
            feedback_content = generate_ai_feedback(evaluation)
            
            feedback = Feedback.objects.create(
                evaluation=evaluation,
                type='ai',
                content=feedback_content['content'],
                strengths=feedback_content.get('strengths', ''),
                improvements=feedback_content.get('improvements', ''),
                recommendations=feedback_content.get('recommendations', ''),
                ai_prompt=feedback_content.get('prompt', ''),
                ai_response=feedback_content,
                created_by=request.user
            )
            
            serializer = self.get_serializer(feedback)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Evaluation.DoesNotExist:
            return Response(
                {'detail': 'Evaluation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GoalViewSet(viewsets.ModelViewSet):
    """ViewSet for Goal CRUD operations"""
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Filter based on user role
        if user.role == 'employee':
            queryset = queryset.filter(employee=user)
        
        # Apply filters
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update goal progress"""
        goal = self.get_object()
        progress = request.data.get('progress', 0)
        notes = request.data.get('achievement_notes', '')
        
        goal.progress = progress
        goal.achievement_notes = notes
        
        # Update status based on progress
        if progress >= 100:
            goal.status = 'achieved'
        elif progress > 0:
            goal.status = 'in_progress'
            
        goal.save()
        
        serializer = self.get_serializer(goal)
        return Response(serializer.data)