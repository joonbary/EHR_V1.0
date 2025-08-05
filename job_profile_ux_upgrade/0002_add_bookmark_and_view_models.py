# Generated migration file
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('job_profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserJobProfileView',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('viewed_at', models.DateTimeField(auto_now=True)),
                ('view_count', models.PositiveIntegerField(default=1)),
                ('job_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='job_profiles.jobprofile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_profile_views', to='auth.user')),
            ],
            options={
                'verbose_name': '직무기술서 조회 기록',
                'verbose_name_plural': '직무기술서 조회 기록',
                'ordering': ['-viewed_at'],
                'unique_together': {('user', 'job_profile')},
            },
        ),
        migrations.CreateModel(
            name='UserJobProfileBookmark',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('job_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarks', to='job_profiles.jobprofile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_profile_bookmarks', to='auth.user')),
            ],
            options={
                'verbose_name': '직무기술서 북마크',
                'verbose_name_plural': '직무기술서 북마크',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'job_profile')},
            },
        ),
    ]
