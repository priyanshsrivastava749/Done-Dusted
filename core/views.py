from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Exam, Subject, Video, Note, UserProfile, DailyStudyLog, CommonNote
from .utils import fetch_playlist_items

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
        
    return render(request, 'dashboard.html', {'exams': exams, 'has_api_key': has_api_key})

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
def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, exam__user=request.user)
    videos = subject.videos.all()
    note, created = Note.objects.get_or_create(subject=subject)
    
    # Calculate progress
    total = videos.count()
    completed = videos.filter(is_watched=True).count()
    progress = (completed / total * 360) if total > 0 else 0
    
    # Daily Progress
    today = timezone.now().date()
    daily_log, _ = DailyStudyLog.objects.get_or_create(user=request.user, subject=subject, date=today)
    today_minutes = round(daily_log.seconds_watched / 60, 1)
    
    return render(request, 'subject_detail.html', {
        'subject': subject,
        'videos': videos,
        'note': note,
        'progress': progress,
        'total': total,
        'completed': completed,
        'today_minutes': today_minutes,
        'daily_goal': subject.daily_goal_minutes
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
    
    return JsonResponse({
        'status': 'ok', 
        'today_minutes': round(daily_log.seconds_watched / 60, 1)
    })

@require_POST
@login_required
def save_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, subject__exam__user=request.user)
    import json
    data = json.loads(request.body)
    note.content = data.get('content', '')
    note.save()
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
    return render(request, 'common_note.html', {'note': note})

@require_POST
@login_required
def save_common_note(request):
    note, created = CommonNote.objects.get_or_create(user=request.user)
    import json
    data = json.loads(request.body)
    note.content = data.get('content', '')
    note.save()
    return JsonResponse({'status': 'ok'})
