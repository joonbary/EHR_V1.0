import openai
from django.conf import settings
from typing import Dict, Any


def generate_ai_feedback(evaluation) -> Dict[str, Any]:
    """
    Generate AI-powered feedback for an evaluation
    
    Args:
        evaluation: Evaluation model instance
        
    Returns:
        Dictionary containing AI-generated feedback
    """
    
    # Set OpenAI API key
    openai.api_key = settings.OPENAI_API_KEY
    
    if not openai.api_key:
        return {
            'content': 'AI feedback generation is not configured. Please set OPENAI_API_KEY in settings.',
            'strengths': '',
            'improvements': '',
            'recommendations': '',
            'prompt': '',
        }
    
    # Prepare evaluation data
    employee_name = evaluation.employee.get_full_name()
    period_name = evaluation.period.name
    overall_score = evaluation.overall_score or 0
    
    # Get scores by category
    scores_data = []
    for score in evaluation.scores.all():
        scores_data.append({
            'category': score.criterion.get_category_display(),
            'criterion': score.criterion.name,
            'score': float(score.score),
            'comment': score.comment
        })
    
    # Get completed tasks
    tasks = evaluation.employee.assigned_tasks.filter(
        start_date__gte=evaluation.period.start_date,
        start_date__lte=evaluation.period.end_date
    )
    completed_tasks = tasks.filter(status='completed').count()
    total_tasks = tasks.count()
    
    # Create prompt for OpenAI
    prompt = f"""
    Generate a comprehensive performance evaluation feedback for the following employee:
    
    Employee: {employee_name}
    Evaluation Period: {period_name}
    Overall Score: {overall_score}/100
    Task Completion Rate: {completed_tasks}/{total_tasks}
    
    Individual Scores:
    {chr(10).join([f"- {s['category']} - {s['criterion']}: {s['score']}/100 (Comment: {s['comment']})" for s in scores_data])}
    
    Please provide:
    1. Overall performance summary
    2. Key strengths (3-5 points)
    3. Areas for improvement (3-5 points)
    4. Specific recommendations for growth
    5. Motivation and encouragement
    
    The feedback should be constructive, professional, and actionable. Write in Korean.
    """
    
    try:
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an experienced HR professional providing constructive performance evaluation feedback. Be specific, actionable, and encouraging."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Parse the response
        ai_content = response.choices[0].message.content
        
        # Extract sections from AI response
        lines = ai_content.split('\n')
        content = []
        strengths = []
        improvements = []
        recommendations = []
        
        current_section = 'content'
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if '강점' in line or '장점' in line or 'strength' in line.lower():
                current_section = 'strengths'
            elif '개선' in line or 'improvement' in line.lower():
                current_section = 'improvements'
            elif '추천' in line or '제안' in line or 'recommendation' in line.lower():
                current_section = 'recommendations'
            else:
                if current_section == 'content':
                    content.append(line)
                elif current_section == 'strengths':
                    if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                        strengths.append(line)
                elif current_section == 'improvements':
                    if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                        improvements.append(line)
                elif current_section == 'recommendations':
                    if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                        recommendations.append(line)
        
        return {
            'content': ai_content,
            'strengths': '\n'.join(strengths),
            'improvements': '\n'.join(improvements),
            'recommendations': '\n'.join(recommendations),
            'prompt': prompt,
            'ai_response': response
        }
        
    except Exception as e:
        # Fallback to template-based feedback if AI fails
        return generate_template_feedback(evaluation, employee_name, overall_score, completed_tasks, total_tasks)


def generate_template_feedback(evaluation, employee_name, overall_score, completed_tasks, total_tasks) -> Dict[str, Any]:
    """
    Generate template-based feedback as fallback
    """
    
    # Determine performance level
    if overall_score >= 90:
        level = "탁월한"
        summary = f"{employee_name}님은 이번 평가 기간 동안 탁월한 성과를 보여주셨습니다."
    elif overall_score >= 80:
        level = "우수한"
        summary = f"{employee_name}님은 이번 평가 기간 동안 우수한 성과를 달성하셨습니다."
    elif overall_score >= 70:
        level = "양호한"
        summary = f"{employee_name}님은 이번 평가 기간 동안 양호한 성과를 보여주셨습니다."
    elif overall_score >= 60:
        level = "보통의"
        summary = f"{employee_name}님은 이번 평가 기간 동안 보통 수준의 성과를 달성하셨습니다."
    else:
        level = "개선이 필요한"
        summary = f"{employee_name}님은 이번 평가 기간 동안 개선이 필요한 부분들이 확인되었습니다."
    
    # Generate strengths based on high scores
    high_scores = []
    for score in evaluation.scores.all():
        if score.score >= 80:
            high_scores.append(f"- {score.criterion.get_category_display()}: {score.criterion.name}")
    
    strengths = "\n".join(high_scores[:5]) if high_scores else "- 성실한 업무 수행\n- 팀워크 기여"
    
    # Generate areas for improvement based on low scores
    low_scores = []
    for score in evaluation.scores.all():
        if score.score < 70:
            low_scores.append(f"- {score.criterion.get_category_display()}: {score.criterion.name}")
    
    improvements = "\n".join(low_scores[:5]) if low_scores else "- 지속적인 역량 개발\n- 새로운 기술 습득"
    
    # Generate recommendations
    recommendations = f"""- 정기적인 1:1 면담을 통한 목표 설정 및 피드백
- 전문 역량 강화를 위한 교육 프로그램 참여
- 멘토링 프로그램 활용
- 업무 프로세스 개선 제안"""
    
    # Complete content
    content = f"""{summary}

전체 평가 점수: {overall_score}/100
업무 완료율: {completed_tasks}/{total_tasks} ({(completed_tasks/total_tasks*100 if total_tasks > 0 else 0):.1f}%)

**주요 강점:**
{strengths}

**개선 필요 영역:**
{improvements}

**성장을 위한 제안:**
{recommendations}

앞으로도 지속적인 성장과 발전을 기대합니다. 궁금한 사항이 있으시면 언제든 상의해 주시기 바랍니다."""
    
    return {
        'content': content,
        'strengths': strengths,
        'improvements': improvements,
        'recommendations': recommendations,
        'prompt': 'Template-based feedback (AI service unavailable)',
    }