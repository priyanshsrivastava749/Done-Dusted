from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/gate/', views.analytics_details, name='analytics_subject'),
    path('analytics/data/', views.get_analytics_data, name='get_analytics_data'),
    path('api_guide/', TemplateView.as_view(template_name='api_guide.html'), name='api_guide'),
    path('save_api/', views.save_api_key, name='save_api_key'),
    path('setup-api-key/', views.setup_api_key, name='setup_api_key'),
    path('create_exam/', views.create_exam, name='create_exam'),
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('subject/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('subject/<int:subject_id>/add_playlist/', views.add_playlist, name='add_playlist'),
    path('subject/<int:subject_id>/add_video/', views.add_video, name='add_video'),
    path('subject/<int:subject_id>/set_goal/', views.set_daily_goal, name='set_daily_goal'),
    path('video/<int:video_id>/status/', views.update_video_status, name='update_video_status'),
    path('chunk/<int:chunk_id>/status/', views.update_chunk_status, name='update_chunk_status'),

    path('exam/<int:exam_id>/delete/', views.delete_exam, name='delete_exam'),
    path('subject/<int:subject_id>/delete/', views.delete_subject, name='delete_subject'),
    path('subject/<int:subject_id>/delete-playlist/', views.delete_playlist, name='delete_playlist'),
    path('subject/<int:subject_id>/import-csv/', views.upload_csv_todo, name='upload_csv_todo'),
    path('api/set-goal/', views.set_global_goal, name='set_global_goal'),
    path('api/get-today-goal/', views.get_today_goal, name='get_today_goal'),
    path('api/save-focus-progress/', views.save_focus_progress, name='save_focus_progress'),
    path('api/timer/start/', views.start_timer, name='start_timer'),
    path('api/timer/stop/', views.stop_timer, name='stop_timer'),
]
