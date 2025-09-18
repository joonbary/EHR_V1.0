#!/usr/bin/env python
"""
URL reverse 테스트 스크립트
"""
import os
import sys
import django

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ehr_evaluation.settings")
    django.setup()
    
    from django.urls import reverse
    
    print("=" * 60)
    print("URL Reverse 테스트")
    print("=" * 60)
    
    urls_to_test = [
        'evaluations:dashboard',
        'evaluations:contribution_guide',
        'evaluations:contribution_employees',
        'evaluations:expertise_guide',
        'evaluations:expertise_employees',
        'evaluations:impact_guide',
        'evaluations:impact_employees',
    ]
    
    for url_name in urls_to_test:
        try:
            resolved_url = reverse(url_name)
            print(f"✅ {url_name:40} -> {resolved_url}")
        except Exception as e:
            print(f"❌ {url_name:40} -> ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("템플릿 태그 테스트")
    print("=" * 60)
    
    from django.template import Template, Context
    
    template_tests = [
        "{% url 'evaluations:contribution_guide' %}",
        "{% url 'evaluations:expertise_guide' %}",
        "{% url 'evaluations:impact_guide' %}",
    ]
    
    for template_str in template_tests:
        try:
            template = Template("{% load i18n %}" + template_str)
            rendered = template.render(Context())
            print(f"✅ {template_str:50} -> {rendered}")
        except Exception as e:
            print(f"❌ {template_str:50} -> ERROR: {e}")