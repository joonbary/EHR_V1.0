#!/bin/bash
# Django ���� ���ε� ��ũ��Ʈ

echo "Django ������� ���� ���� ��..."

# 1. Python ĳ�� ����
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# 2. ���̱׷��̼� ���� ����� (�ʿ��)
# python manage.py makemigrations
# python manage.py migrate

# 3. Static ���� �����
python manage.py collectstatic --noinput --clear

# 4. ���� �����
echo ""
echo "���� ������ ������ϼ���:"
echo "python manage.py runserver"
