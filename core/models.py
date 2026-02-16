from django.db import models
from django.contrib.auth.models import User
import os
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    google_api_key = models.CharField(max_length=255, blank=True, null=True, help_text="Your YouTube Data API Key")
    current_streak = models.PositiveIntegerField(default=0)
    last_goal_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Exam(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exams')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='subjects')
    daily_goal_minutes = models.PositiveIntegerField(default=0, help_text="Daily study goal in minutes")
    
    def __str__(self):
        return self.name

class Video(models.Model):
    title = models.CharField(max_length=255)
    video_id = models.CharField(max_length=50) # YouTube Video ID
    url = models.URLField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='videos')
    is_watched = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    duration_seconds = models.PositiveIntegerField(default=0)
    
    # New Chunking Support
    is_chunked = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    @property
    def duration_display(self):
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        if seconds > 0:
            return f"{minutes}m {seconds}s"
        return f"{minutes}m"

    def __str__(self):
        return self.title

class VideoChunk(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='chunks')
    part_number = models.PositiveIntegerField()
    title = models.CharField(max_length=100) # e.g. "Part 1 (00:00 - 20:00)"
    start_seconds = models.PositiveIntegerField()
    end_seconds = models.PositiveIntegerField()
    is_watched = models.BooleanField(default=False)

    class Meta:
        ordering = ['part_number']

    def __str__(self):
        return f"{self.video.title} - {self.title}"

class Note(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField(blank=True, help_text="Markdown/HTML content with LaTeX support")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notes for {self.subject.name}"
    
    def get_file_path(self):
        # Path: media/notes/subjects/<subject_id>/note.html
        return os.path.join(settings.MEDIA_ROOT, 'notes', 'subjects', str(self.subject.id), 'note.html')

    def save_content_to_file(self, content):
        file_path = self.get_file_path()
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def get_content_from_file(self):
        file_path = self.get_file_path()
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return self.content # Fallback to DB

from django.utils import timezone

class DailyStudyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_logs')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='study_logs')
    date = models.DateField(default=timezone.now)
    seconds_watched = models.PositiveIntegerField(default=0)
    daily_goal_minutes = models.PositiveIntegerField(default=0)
    goal_achieved = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'subject', 'date']

    def __str__(self):
        return f"{self.user.username} - {self.subject.name} - {self.date}"

class CommonNote(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='common_note')
    content = models.TextField(blank=True, help_text="Common scratchpad content")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Common Note for {self.user.username}"

    def get_file_path(self):
        # Path: media/notes/users/<user_id>/common_note.html
        return os.path.join(settings.MEDIA_ROOT, 'notes', 'users', str(self.user.id), 'common_note.html')

    def save_content_to_file(self, content):
        file_path = self.get_file_path()
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def get_content_from_file(self):
        file_path = self.get_file_path()
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return self.content # Fallback to DB

class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    total_seconds = models.PositiveIntegerField(default=0)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Pro Session - {self.user.username} - {self.date}"

class DailyGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_goals')
    date = models.DateField(default=timezone.now)
    goal_hours = models.FloatField()
    completed_seconds = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    achieved = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'date']

    def __str__(self):
        return f"Goal - {self.user.username} - {self.date}"

class Streak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.PositiveIntegerField(default=0)
    best_streak = models.PositiveIntegerField(default=0)
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"Streak - {self.user.username} - {self.current_streak}"

# --- SIGNALS ---
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


