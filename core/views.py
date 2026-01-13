from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Exam, Subject, Video, Note, UserProfile, DailyStudyLog, CommonNote, StudySession, DailyGoal, Streak
from .utils import fetch_playlist_items
import os

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user) # Create empty profile
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    exams = request.user.exams.all()
    # Check if user has API key (Env or DB)
    from django.conf import settings
    env_key = getattr(settings, 'GOOGLE_API_KEY', None)
    if env_key == 'YOUR_API_KEY_HERE':
        env_key = None
    
    try:
        profile_key = request.user.profile.google_api_key
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=request.user)
        profile_key = None
        
    has_api_key = bool(env_key or profile_key)
        

    user_goals = []
    for exam in exams:
        watched_seconds = Video.objects.filter(
            subject__exam=exam, 
            is_watched=True
        ).aggregate(models.Sum('duration_seconds'))['duration_seconds__sum'] or 0
        
        user_goals.append({
            'name': exam.name,
            'total_hours': round(watched_seconds / 3600, 1)
        })

    today = timezone.now().date()
    todays_goal = DailyGoal.objects.filter(user=request.user, date=today).first()
    show_modal = not todays_goal
    streak, _ = Streak.objects.get_or_create(user=request.user)
    
    context = {
        'exams': exams,
        'user_goals': user_goals,
        'has_api_key': has_api_key,
        'todays_goal': todays_goal,
        'show_modal': show_modal,
        'streak': streak,
    }
    return render(request, 'dashboard.html', context)


@login_required
def get_analytics_data(request):
    exams = Exam.objects.filter(user=request.user).prefetch_related('subjects')
    analytics_data = []
    
    for exam in exams:
        subjects_data = []
        exam_total_seconds = 0
        
        for subject in exam.subjects.all():
            watched_seconds = Video.objects.filter(
                subject=subject,
                is_watched=True
            ).aggregate(models.Sum('duration_seconds'))['duration_seconds__sum'] or 0
            
            exam_total_seconds += watched_seconds
            
            if watched_seconds > 0:
                subjects_data.append({
                    'name': subject.name,
                    'seconds': watched_seconds,
                    'hours': round(watched_seconds / 3600, 1)
                })
        
        # Calculate percentages
        for sub in subjects_data:
            sub['percentage'] = round((sub['seconds'] / exam_total_seconds) * 100, 1) if exam_total_seconds > 0 else 0
            
        analytics_data.append({
            'goal_name': exam.name,
            'total_hours': round(exam_total_seconds / 3600, 1),
            'subjects': sorted(subjects_data, key=lambda x: x['hours'], reverse=True)
        })
        
    return JsonResponse({'status': 'ok', 'data': analytics_data})

@login_required
def analytics_details(request):

    exams = Exam.objects.filter(user=request.user).prefetch_related('subjects')
    
    analytics_data = []
    
    for exam in exams:
        subjects_data = []
        exam_total_seconds = 0
        
        for subject in exam.subjects.all():
            watched_seconds = Video.objects.filter(
                subject=subject,
                is_watched=True
            ).aggregate(models.Sum('duration_seconds'))['duration_seconds__sum'] or 0
            
            exam_total_seconds += watched_seconds
            
            if watched_seconds > 0:
                subjects_data.append({
                    'name': subject.name,
                    'seconds': watched_seconds,
                    'hours': round(watched_seconds / 3600, 1)
                })
        
        # Calculate percentages
        for sub in subjects_data:
            sub['percentage'] = round((sub['seconds'] / exam_total_seconds) * 100, 1) if exam_total_seconds > 0 else 0
            
        analytics_data.append({
            'goal_name': exam.name,
            'total_hours': round(exam_total_seconds / 3600, 1),
            'subjects': sorted(subjects_data, key=lambda x: x['hours'], reverse=True)
        })
        
    return render(request, 'analytics_subject.html', {'analytics_data': analytics_data})

@login_required
def save_api_key(request):
    if request.method == 'POST':
        key = request.POST.get('api_key')
        if key:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.google_api_key = key
            profile.save()
    return redirect('dashboard')

@login_required
def create_exam(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Exam.objects.create(user=request.user, name=name)
        return redirect('dashboard')
    return render(request, 'create_exam.html')

@login_required
def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, user=request.user)
    subjects = exam.subjects.all()
    if request.method == 'POST': # Create Subject
        sub_name = request.POST.get('name')
        if sub_name:
            Subject.objects.create(exam=exam, name=sub_name)
            return redirect('exam_detail', exam_id=exam.id)
    return render(request, 'exam_detail.html', {'exam': exam, 'subjects': subjects})

@login_required
def get_note_content(request, note_id):
    note = get_object_or_404(Note, id=note_id, subject__exam__user=request.user)
    note_type = request.GET.get('type', 'content')
    
    if note_type == 'screenshots':
        file_path = note.get_screenshots_file_path()
    else:
        file_path = note.get_file_path()
        
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'))
    return HttpResponse("")

@login_required
def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, exam__user=request.user)
    
    # Optimize: Fetch all videos once, calculate stats in python
    videos = list(subject.videos.all()) 
    total = len(videos)
    completed = sum(1 for v in videos if v.is_watched)
    
    note, created = Note.objects.get_or_create(subject=subject)
    # CONTENT LOAD REMOVED - Handled by lazy loading via get_note_content
    
    progress = (completed / total * 360) if total > 0 else 0
    
    # Daily Progress
    today = timezone.now().date()
    daily_log, _ = DailyStudyLog.objects.get_or_create(user=request.user, subject=subject, date=today)
    today_minutes = round(daily_log.seconds_watched / 60, 1)
    
    # Playlist Stats (Hours)
    total_seconds_watched = sum(v.duration_seconds for v in videos if v.is_watched)
    total_seconds_left = sum(v.duration_seconds for v in videos if not v.is_watched)
    
    watched_hours = "{:.2f}".format(total_seconds_watched / 3600)
    left_hours = "{:.2f}".format(total_seconds_left / 3600)

    return render(request, 'subject_detail.html', {
        'subject': subject,
        'videos': videos,
        'note': note,
        'progress': progress,
        'total': total,
        'completed': completed,
        'today_minutes': today_minutes,
        'daily_goal': subject.daily_goal_minutes,
        'remaining_goal': max(0, subject.daily_goal_minutes - today_minutes),
        'watched_hours': watched_hours,
        'left_hours': left_hours,
    })

@login_required
def add_playlist(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, exam__user=request.user)
    if request.method == 'POST':
        url = request.POST.get('playlist_url')
        
        from django.conf import settings
        img_key = getattr(settings, 'GOOGLE_API_KEY', None)
        if img_key == 'YOUR_API_KEY_HERE':
            img_key = None
            
        profile_key = request.user.profile.google_api_key
        api_key = img_key if img_key else profile_key
        
        if not api_key:
            # Should handle better, but for now redirect
            return redirect('dashboard')
            
        videos_data = fetch_playlist_items(url, api_key)
        if videos_data:
            for idx, vid in enumerate(videos_data):
                Video.objects.create(
                    subject=subject,
                    title=vid['title'],
                    video_id=vid['video_id'],
                    url=vid['url'],
                    order=idx,
                    duration_seconds=vid.get('duration', 0)
                )
    return redirect('subject_detail', subject_id=subject.id)

@require_POST
@login_required
def update_video_status(request, video_id):
    video = get_object_or_404(Video, id=video_id, subject__exam__user=request.user)
    import json
    data = json.loads(request.body)
    video.is_watched = data.get('is_watched', False)
    video.save()
    
    # Update Daily Log
    today = timezone.now().date()
    # Ensure log exists for this specific subject
    daily_log, _ = DailyStudyLog.objects.get_or_create(
        user=request.user, 
        subject=video.subject, 
        date=today
    )
    
    if video.is_watched:
        daily_log.seconds_watched += video.duration_seconds
    else:
        # Prevent negative values if unchecking
        daily_log.seconds_watched = max(0, daily_log.seconds_watched - video.duration_seconds)
    
    daily_log.save()
    today_minutes = round(daily_log.seconds_watched / 60, 1)

    # --- Live Analytics Calculation ---
    # We want to return the updated total hours for ALL exams to update any listeners
    all_exams = Exam.objects.filter(user=request.user)
    analytics_response = {}
    
    for exam in all_exams:
        total_seconds = Video.objects.filter(
            subject__exam=exam, 
            is_watched=True
        ).aggregate(models.Sum('duration_seconds'))['duration_seconds__sum'] or 0
        analytics_response[exam.name] = round(total_seconds / 3600, 1)
    
    return JsonResponse({
        'status': 'ok', 
        'today_minutes': today_minutes,
        'remaining_goal': max(0, video.subject.daily_goal_minutes - today_minutes),
        'analytics': analytics_response
    })

@require_POST
@login_required
def save_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, subject__exam__user=request.user)
    import json
    data = json.loads(request.body)
    note_type = data.get('note_type', 'content')
    
    if note_type == 'screenshots':
        note.save_screenshots_to_file(data.get('content', ''))
    else:
        note.save_content_to_file(data.get('content', ''))
        
    note.save() # Update timestamp
    return JsonResponse({'status': 'ok'})

@require_POST
@login_required
def set_daily_goal(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, exam__user=request.user)
    try:
        minutes = int(request.POST.get('minutes', 0))
        subject.daily_goal_minutes = minutes
        subject.save()
    except ValueError:
        pass
    return redirect('subject_detail', subject_id=subject.id)

@login_required
def common_note_view(request):
    note, created = CommonNote.objects.get_or_create(user=request.user)
    # Load content from file
    note.content = note.get_content_from_file()
    return render(request, 'common_note.html', {'note': note})

@require_POST
@login_required
def save_common_note(request):
    note, created = CommonNote.objects.get_or_create(user=request.user)
    import json
    data = json.loads(request.body)
    note.save_content_to_file(data.get('content', ''))
    note.save() # Update timestamp
    return JsonResponse({'status': 'ok'})
@login_required
def get_today_goal(request):
    today = timezone.now().date()
    # Try to find existing goal
    daily_goal = DailyGoal.objects.filter(user=request.user, date=today).first()
    
    if not daily_goal:
        return JsonResponse({'status': 'no_goal', 'message': 'No goal set for today.'})
    
    goal_seconds = int(daily_goal.goal_hours * 3600)
    
    return JsonResponse({
        'status': 'ok',
        'goal_seconds': goal_seconds,
        'completed_seconds': daily_goal.completed_seconds, 
        'is_completed': daily_goal.is_completed,
        'remaining_seconds': max(0, goal_seconds - daily_goal.completed_seconds)
    })

@require_POST
@login_required
def save_focus_progress(request):
    import json
    data = json.loads(request.body)
    new_seconds = int(data.get('seconds', 0)) # This is incremental seconds to ADD
    
    today = timezone.now().date()
    daily_goal = DailyGoal.objects.filter(user=request.user, date=today).first()
    
    if not daily_goal:
        return JsonResponse({'status': 'error', 'message': 'No goal found'})
        
    daily_goal.completed_seconds += new_seconds
    
    # Check completion
    goal_seconds = int(daily_goal.goal_hours * 3600)
    if daily_goal.completed_seconds >= goal_seconds and not daily_goal.is_completed:
        daily_goal.is_completed = True
        daily_goal.achieved = True
        
        # Streak Update
        streak, _ = Streak.objects.get_or_create(user=request.user)
        # Assuming achieving daily goal increments streak? 
        # Previous logic might handle streaks differently, but let's ensure it's marked "achieved"
        pass 

    daily_goal.save()
    
    return JsonResponse({
        'status': 'ok',
        'completed_seconds': daily_goal.completed_seconds,
        'is_completed': daily_goal.is_completed
    })

@require_POST
@login_required
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, user=request.user)
    exam.delete()
    return redirect('dashboard')

@require_POST
@login_required
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, exam__user=request.user)
    exam_id = subject.exam.id
    subject.delete()
    return redirect('exam_detail', exam_id=exam_id)

@require_POST
@login_required
def delete_playlist(request, subject_id):
    subject.videos.all().delete()
    return redirect('subject_detail', subject_id=subject.id)

@require_POST
@login_required
def set_global_goal(request):
    import json
    data = json.loads(request.body)
    hours = float(data.get('hours', 0))
    today = timezone.now().date()
    
    obj, created = DailyGoal.objects.get_or_create(user=request.user, date=today, defaults={'goal_hours': hours})
    if not created:
        return JsonResponse({'status': 'exists', 'message': 'Goal already set for today!'})
        
    return JsonResponse({'status': 'ok'})

@require_POST
@login_required
def update_goal_status(request):
    # Check if goal calculated dynamically or manually?
    # Usually strictly time based.
    pass 

@require_POST
@login_required
def start_timer(request):
    # End any running sessions first?
    StudySession.objects.filter(user=request.user, end_time__isnull=True).update(end_time=timezone.now())
    
    StudySession.objects.create(
        user=request.user,
        start_time=timezone.now()
    )
    return JsonResponse({'status': 'started'})

@require_POST
@login_required
def stop_timer(request):
    session = StudySession.objects.filter(user=request.user, end_time__isnull=True).last()
    if session:
        session.end_time = timezone.now()
        diff = (session.end_time - session.start_time).total_seconds()
        session.total_seconds = int(diff)
        session.save()
        
        # Check daily goal achievement (Global timer + Video time?)
        # For now just log it.
        return JsonResponse({'status': 'stopped', 'seconds': session.total_seconds})
    return JsonResponse({'status': 'error', 'message': 'No running session'})

