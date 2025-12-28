from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    google_api_key = models.CharField(max_length=255, blank=True, null=True, help_text="Your YouTube Data API Key")

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
    
    def __str__(self):
        return self.name

class Video(models.Model):
    title = models.CharField(max_length=255)
    video_id = models.CharField(max_length=50) # YouTube Video ID
    url = models.URLField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='videos')
    is_watched = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Note(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField(blank=True, help_text="Markdown/HTML content with LaTeX support")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notes for {self.subject.name}"
