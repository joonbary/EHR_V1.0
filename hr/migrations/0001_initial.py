# Generated manually for HR app
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True, verbose_name='직군 코드')),
                ('name', models.CharField(max_length=50, verbose_name='직군명')),
                ('description', models.TextField(blank=True, verbose_name='설명')),
                ('sort_order', models.IntegerField(default=0, verbose_name='정렬순서')),
                ('is_active', models.BooleanField(default=True, verbose_name='활성화')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '직군',
                'verbose_name_plural': '직군',
                'ordering': ['sort_order', 'name'],
                'db_table': 'hr_job_groups',
            },
        ),
        migrations.CreateModel(
            name='JobCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True, verbose_name='직종 코드')),
                ('name', models.CharField(max_length=50, verbose_name='직종명')),
                ('description', models.TextField(blank=True, verbose_name='설명')),
                ('sort_order', models.IntegerField(default=0, verbose_name='정렬순서')),
                ('is_active', models.BooleanField(default=True, verbose_name='활성화')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('job_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='hr.jobgroup', verbose_name='직군')),
            ],
            options={
                'verbose_name': '직종',
                'verbose_name_plural': '직종',
                'ordering': ['job_group', 'sort_order', 'name'],
                'db_table': 'hr_job_categories',
            },
        ),
        migrations.CreateModel(
            name='JobRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True, verbose_name='직무 코드')),
                ('name', models.CharField(max_length=50, verbose_name='직무명')),
                ('description', models.TextField(blank=True, verbose_name='설명')),
                ('required_skills', models.TextField(blank=True, verbose_name='필수 역량')),
                ('sort_order', models.IntegerField(default=0, verbose_name='정렬순서')),
                ('is_active', models.BooleanField(default=True, verbose_name='활성화')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('job_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='hr.jobcategory', verbose_name='직종')),
            ],
            options={
                'verbose_name': '직무',
                'verbose_name_plural': '직무',
                'ordering': ['job_category', 'sort_order', 'name'],
                'db_table': 'hr_job_roles',
            },
        ),
        migrations.CreateModel(
            name='JobGrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True, verbose_name='직급 코드')),
                ('name', models.CharField(max_length=50, verbose_name='직급명')),
                ('level', models.IntegerField(verbose_name='레벨')),
                ('min_experience_years', models.IntegerField(default=0, verbose_name='최소 경력년수')),
                ('sort_order', models.IntegerField(default=0, verbose_name='정렬순서')),
                ('is_active', models.BooleanField(default=True, verbose_name='활성화')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '직급',
                'verbose_name_plural': '직급',
                'ordering': ['level', 'sort_order'],
                'db_table': 'hr_job_grades',
            },
        ),
        migrations.CreateModel(
            name='EmploymentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True, verbose_name='고용형태 코드')),
                ('name', models.CharField(max_length=50, verbose_name='고용형태명')),
                ('is_permanent', models.BooleanField(default=True, verbose_name='정규직 여부')),
                ('sort_order', models.IntegerField(default=0, verbose_name='정렬순서')),
                ('is_active', models.BooleanField(default=True, verbose_name='활성화')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '고용형태',
                'verbose_name_plural': '고용형태',
                'ordering': ['sort_order', 'name'],
                'db_table': 'hr_employment_types',
            },
        ),
        migrations.CreateModel(
            name='BaseSalary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_amount', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='기본급')),
                ('effective_date', models.DateField(verbose_name='적용시작일')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='적용종료일')),
                ('is_active', models.BooleanField(default=True, verbose_name='활성화')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='base_salaries', to='employees.employee', verbose_name='직원')),
                ('job_grade', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='hr.jobgrade', verbose_name='직급')),
            ],
            options={
                'verbose_name': '기본급',
                'verbose_name_plural': '기본급',
                'ordering': ['-effective_date'],
                'db_table': 'hr_base_salaries',
            },
        ),
        # Add other model definitions as needed...
    ]