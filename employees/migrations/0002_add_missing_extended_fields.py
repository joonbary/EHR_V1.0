# Generated manually to add all missing Employee model fields

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add missing basic fields
        migrations.AddField(
            model_name='employee',
            name='no',
            field=models.IntegerField(blank=True, null=True, verbose_name='NO'),
        ),
        migrations.AddField(
            model_name='employee',
            name='company',
            field=models.CharField(blank=True, choices=[('OK', 'OK'), ('OCI', 'OCI'), ('OC', 'OC'), ('OFI', 'OFI'), ('OKDS', 'OKDS'), ('OKH', 'OKH'), ('ON', 'ON'), ('OKIP', 'OKIP'), ('OT', 'OT'), ('OKV', 'OKV'), ('EX', 'EX')], max_length=10, null=True, verbose_name='회사'),
        ),
        migrations.AddField(
            model_name='employee',
            name='previous_position',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='직급(전)'),
        ),
        migrations.AddField(
            model_name='employee',
            name='current_position',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='직급'),
        ),
        
        # Add organization structure fields
        migrations.AddField(
            model_name='employee',
            name='headquarters1',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='본부1'),
        ),
        migrations.AddField(
            model_name='employee',
            name='headquarters2',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='본부2'),
        ),
        migrations.AddField(
            model_name='employee',
            name='department1',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='소속1'),
        ),
        migrations.AddField(
            model_name='employee',
            name='department2',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='소속2'),
        ),
        migrations.AddField(
            model_name='employee',
            name='department3',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='소속3'),
        ),
        migrations.AddField(
            model_name='employee',
            name='department4',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='소속4'),
        ),
        migrations.AddField(
            model_name='employee',
            name='final_department',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='최종소속'),
        ),
        
        # Add job-related fields
        migrations.AddField(
            model_name='employee',
            name='job_series',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='직군/계열'),
        ),
        migrations.AddField(
            model_name='employee',
            name='title',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='호칭'),
        ),
        migrations.AddField(
            model_name='employee',
            name='responsibility',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='직책'),
        ),
        migrations.AddField(
            model_name='employee',
            name='promotion_level',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='승급레벨'),
        ),
        migrations.AddField(
            model_name='employee',
            name='salary_grade',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='급호'),
        ),
        
        # Add personal information fields
        migrations.AddField(
            model_name='employee',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', '남성'), ('F', '여성')], max_length=1, null=True, verbose_name='성별'),
        ),
        migrations.AddField(
            model_name='employee',
            name='age',
            field=models.IntegerField(blank=True, null=True, verbose_name='나이'),
        ),
        migrations.AddField(
            model_name='employee',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='생일'),
        ),
        
        # Add date fields
        migrations.AddField(
            model_name='employee',
            name='group_join_date',
            field=models.DateField(blank=True, null=True, verbose_name='그룹입사일'),
        ),
        migrations.AddField(
            model_name='employee',
            name='career_join_date',
            field=models.DateField(blank=True, null=True, verbose_name='경력입사일'),
        ),
        migrations.AddField(
            model_name='employee',
            name='new_join_date',
            field=models.DateField(blank=True, null=True, verbose_name='신입입사일'),
        ),
        
        # Add evaluation and work-related fields
        migrations.AddField(
            model_name='employee',
            name='promotion_accumulated_years',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='승급누적년수'),
        ),
        migrations.AddField(
            model_name='employee',
            name='final_evaluation',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='최종평가'),
        ),
        
        # Add tag fields
        migrations.AddField(
            model_name='employee',
            name='job_tag_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='직무태그명'),
        ),
        migrations.AddField(
            model_name='employee',
            name='rank_tag_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='순위태그명'),
        ),
        
        # Add additional fields
        migrations.AddField(
            model_name='employee',
            name='education',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='학력'),
        ),
        migrations.AddField(
            model_name='employee',
            name='marital_status',
            field=models.CharField(blank=True, choices=[('Y', '기혼'), ('N', '미혼'), ('D', '이혼'), ('W', '사별')], max_length=1, null=True, verbose_name='결혼여부'),
        ),
        migrations.AddField(
            model_name='employee',
            name='job_family',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='직무군'),
        ),
        migrations.AddField(
            model_name='employee',
            name='job_field',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='직무분야'),
        ),
        migrations.AddField(
            model_name='employee',
            name='classification',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='분류'),
        ),
        migrations.AddField(
            model_name='employee',
            name='current_headcount',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='현원'),
        ),
        migrations.AddField(
            model_name='employee',
            name='detailed_classification',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='세부분류'),
        ),
        migrations.AddField(
            model_name='employee',
            name='category',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='구분'),
        ),
        migrations.AddField(
            model_name='employee',
            name='diversity_years',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='다양성년수'),
        ),
        
        # Add dummy fields that are already in the database (these will be skipped if they exist)
        migrations.AddField(
            model_name='employee',
            name='dummy_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='이름(익명화)'),
        ),
        migrations.AddField(
            model_name='employee',
            name='dummy_mobile',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='휴대폰(익명화)'),
        ),
        migrations.AddField(
            model_name='employee',
            name='dummy_registered_address',
            field=models.TextField(blank=True, null=True, verbose_name='주민등록주소(익명화)'),
        ),
        migrations.AddField(
            model_name='employee',
            name='dummy_residence_address',
            field=models.TextField(blank=True, null=True, verbose_name='실거주지주소(익명화)'),
        ),
        migrations.AddField(
            model_name='employee',
            name='dummy_email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='이메일(익명화)'),
        ),
    ]