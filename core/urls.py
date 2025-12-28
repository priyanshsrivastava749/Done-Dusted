from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api_guide/', TemplateView.as_view(template_name='api_guide.html'), name='api_guide'),
    path('save_api/', views.save_api_key, name='save_api_key'),
    path('create_exam/', views.create_exam, name='create_exam'),
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('subject/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('subject/<int:subject_id>/add_playlist/', views.add_playlist, name='add_playlist'),
    path('video/<int:video_id>/status/', views.update_video_status, name='update_video_status'),
    path('note/<int:note_id>/save/', views.save_note, name='save_note'),
]
