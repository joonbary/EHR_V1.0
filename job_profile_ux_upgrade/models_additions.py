# job_profiles/models.py에 추가할 모델

class UserJobProfileBookmark(models.Model):
    """사용자 직무기술서 북마크"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_profile_bookmarks')
    job_profile = models.ForeignKey(JobProfile, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = '직무기술서 북마크'
        verbose_name_plural = '직무기술서 북마크'
        unique_together = ['user', 'job_profile']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.job_profile.job_role.name}"


class UserJobProfileView(models.Model):
    """사용자 직무기술서 조회 기록"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_profile_views')
    job_profile = models.ForeignKey(JobProfile, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = '직무기술서 조회 기록'
        verbose_name_plural = '직무기술서 조회 기록'
        unique_together = ['user', 'job_profile']
        ordering = ['-viewed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.job_profile.job_role.name} ({self.view_count}회)"
