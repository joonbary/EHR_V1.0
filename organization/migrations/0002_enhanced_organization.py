"""
Migration for Enhanced Organization Models
"""
from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrgUnit',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='조직 ID')),
                ('company', models.CharField(choices=[('OK저축은행', 'OK저축은행'), ('OK캐피탈', 'OK캐피탈'), ('OK금융그룹', 'OK금융그룹'), ('ALL', '전체')], db_index=True, max_length=50, verbose_name='회사')),
                ('name', models.CharField(max_length=100, verbose_name='조직명')),
                ('function', models.CharField(blank=True, help_text='HR, IT, Finance 등', max_length=100, verbose_name='기능')),
                ('headcount', models.IntegerField(default=0, verbose_name='인원수')),
                ('leader_title', models.CharField(blank=True, max_length=50, verbose_name='리더 직책')),
                ('leader_rank', models.CharField(blank=True, max_length=50, verbose_name='리더 직급')),
                ('leader_name', models.CharField(blank=True, max_length=100, verbose_name='리더 성명')),
                ('leader_age', models.IntegerField(blank=True, null=True, verbose_name='리더 나이')),
                ('members', models.JSONField(blank=True, default=list, help_text='[{"grade": "차장", "count": 3}, {"grade": "대리", "count": 5}]', verbose_name='구성원')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_org_units', to=settings.AUTH_USER_MODEL)),
                ('reports_to', models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subordinates', to='organization.orgunit', verbose_name='상위 조직')),
            ],
            options={
                'verbose_name': '조직 단위',
                'verbose_name_plural': '조직 단위',
                'ordering': ['company', 'name'],
            },
        ),
        migrations.CreateModel(
            name='OrgScenario',
            fields=[
                ('scenario_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='시나리오 ID')),
                ('name', models.CharField(max_length=200, verbose_name='시나리오명')),
                ('payload', models.JSONField(default=list, help_text='조직 단위 배열', verbose_name='시나리오 데이터')),
                ('description', models.TextField(blank=True, verbose_name='설명')),
                ('tags', models.CharField(blank=True, max_length=200, verbose_name='태그')),
                ('is_active', models.BooleanField(default=False, verbose_name='활성 시나리오')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='org_scenarios', to=settings.AUTH_USER_MODEL, verbose_name='작성자')),
            ],
            options={
                'verbose_name': '조직 시나리오',
                'verbose_name_plural': '조직 시나리오',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrgSnapshot',
            fields=[
                ('snapshot_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='스냅샷 ID')),
                ('name', models.CharField(max_length=200, verbose_name='스냅샷명')),
                ('snapshot_type', models.CharField(choices=[('CURRENT', '현재 상태'), ('WHATIF', 'What-if 분석'), ('BACKUP', '백업'), ('COMPARISON', '비교용')], default='WHATIF', max_length=20, verbose_name='스냅샷 유형')),
                ('data', models.JSONField(default=list, verbose_name='스냅샷 데이터')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='생성자')),
                ('scenario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='snapshots', to='organization.orgscenario', verbose_name='관련 시나리오')),
            ],
            options={
                'verbose_name': '조직 스냅샷',
                'verbose_name_plural': '조직 스냅샷',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrgChangeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('CREATE', '생성'), ('UPDATE', '수정'), ('DELETE', '삭제'), ('REORG', '재편'), ('IMPORT', '임포트'), ('EXPORT', '익스포트'), ('WHATIF', 'What-if 분석'), ('SCENARIO', '시나리오 적용')], max_length=20, verbose_name='액션')),
                ('org_unit_id', models.CharField(blank=True, max_length=50, null=True, verbose_name='대상 조직 ID')),
                ('changes', models.JSONField(default=dict, verbose_name='변경 내역')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP 주소')),
                ('user_agent', models.TextField(blank=True, verbose_name='User Agent')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='수행자')),
            ],
            options={
                'verbose_name': '조직 변경 로그',
                'verbose_name_plural': '조직 변경 로그',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='orgunit',
            index=models.Index(fields=['company'], name='organizatio_company_d0f8a9_idx'),
        ),
        migrations.AddIndex(
            model_name='orgunit',
            index=models.Index(fields=['reports_to'], name='organizatio_reports_7e6a8f_idx'),
        ),
        migrations.AddIndex(
            model_name='orgunit',
            index=models.Index(fields=['function'], name='organizatio_functio_9c3e4d_idx'),
        ),
        migrations.AddIndex(
            model_name='orgunit',
            index=models.Index(fields=['company', 'name'], name='organizatio_company_3b2c8a_idx'),
        ),
        migrations.AddConstraint(
            model_name='orgunit',
            constraint=models.CheckConstraint(check=models.Q(('id', models.F('reports_to')), _negated=True), name='prevent_self_reporting'),
        ),
        migrations.AddIndex(
            model_name='orgscenario',
            index=models.Index(fields=['-created_at'], name='organizatio_created_8f3a2b_idx'),
        ),
        migrations.AddIndex(
            model_name='orgscenario',
            index=models.Index(fields=['author', '-created_at'], name='organizatio_author__c7d9f3_idx'),
        ),
        migrations.AddIndex(
            model_name='orgchangelog',
            index=models.Index(fields=['-created_at'], name='organizatio_created_4e2b1c_idx'),
        ),
        migrations.AddIndex(
            model_name='orgchangelog',
            index=models.Index(fields=['user', '-created_at'], name='organizatio_user_id_9a3f7e_idx'),
        ),
        migrations.AddIndex(
            model_name='orgchangelog',
            index=models.Index(fields=['action', '-created_at'], name='organizatio_action_7c8e4d_idx'),
        ),
    ]