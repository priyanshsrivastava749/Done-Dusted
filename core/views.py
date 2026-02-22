from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Exam, Subject, Video, Note, UserProfile, DailyStudyLog, CommonNote, StudySession, DailyGoal, Streak, VideoChunk
from .utils import fetch_playlist_items, fetch_video_details
import os
import requests

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # UserProfile created by signal
            login(request, user)
            return redirect('setup_api_key')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def setup_api_key(request):
    error = None
    if request.method == 'POST':
        key = request.POST.get('api_key', '').strip()
        if not key:
            error = "API Key cannot be empty."
        else:
            # Validate Key with a simple list request
            try:
                test_url = "https://www.googleapis.com/youtube/v3/videos?part=snippet&chart=mostPopular&maxResults=1&key=" + key
                response = requests.get(test_url)
                data = response.json()
                
                if 'error' in data:
                    reason = data['error'].get('errors', [{}])[0].get('reason', 'Unknown')
                    if reason == 'quotaExceeded':
                         error = "This key has exceeded its quota."
                    elif reason == 'keyInvalid':
                         error = "Invalid API Key."
                    else:
                         error = f"API Error: {data['error']['message']}"
                else:
                    # Valid!
                    profile, _ = UserProfile.objects.get_or_create(user=request.user)
                    profile.google_api_key = key
                    profile.save()
                    return redirect('dashboard')
            except Exception as e:
                error = f"Network Error: {str(e)}"
    
    return render(request, 'setup_api_key.html', {'error': error})

@login_required
def dashboard(request):
    exams = request.user.exams.all()
    # API Key check handled by middleware now.
    
    skill_analytics = [] 

    today = timezone.localdate()
    todays_goal = DailyGoal.objects.filter(user=request.user, date=today).first()
    show_modal = not todays_goal
    streak, _ = Streak.objects.get_or_create(user=request.user)
    
    # Check for streak reset (if yesterday goal missed)
    profile = request.user.profile
    
    # Logic: If last goal achieved was before yesterday, reset streak.
    if profile.last_goal_date and profile.last_goal_date < (today - timezone.timedelta(days=1)):
        profile.current_streak = 0
        profile.save()
        streak.current_streak = 0
        streak.save()
    
    context = {
        'exams': exams,
        'skill_analytics': skill_analytics,
        'has_api_key': True, # Middleware guarantees this
        'todays_goal': todays_goal,
        'show_modal': show_modal,
        'streak': streak,
    }
    return render(request, 'dashboard.html', context)


@login_required
def analytics_dashboard(request):
    analytics_data = []
    
    # 1. Fetch Goals (Exams)
    goals = Exam.objects.filter(user=request.user).prefetch_related('subjects')
    
    for goal in goals:
        goal_total_seconds = 0
        subjects_data = []
        
        # 2. Iterate Subjects
        for subject in goal.subjects.all():
            # Calculate Chunk Hours
            chunk_seconds = VideoChunk.objects.filter(
                video__subject=subject,
                is_watched=True
            ).aggregate(
                total=models.Sum(models.F('end_seconds') - models.F('start_seconds'))
            )['total'] or 0
            
            # Calculate Whole Video Hours (exclude chunked videos)
            video_seconds = Video.objects.filter(
                subject=subject,
                is_watched=True,
                is_chunked=False
            ).aggregate(
                total=models.Sum('duration_seconds')
            )['total'] or 0
            
            subject_total_seconds = chunk_seconds + video_seconds
            goal_total_seconds += subject_total_seconds
            
            if subject_total_seconds > 0:
                subjects_data.append({
                    'name': subject.name,
                    'seconds': subject_total_seconds,
                    'hours': round(subject_total_seconds / 3600, 1)
                })
        
        # 3. Calculate Percentages
        for sub in subjects_data:
            sub['percent'] = round((sub['seconds'] / goal_total_seconds) * 100, 1) if goal_total_seconds > 0 else 0
            
        # Sort subjects by contribution (optional but nice)
        subjects_data.sort(key=lambda x: x['seconds'], reverse=True)
        
        analytics_data.append({
            'goal_name': goal.name,
            'total_hours': round(goal_total_seconds / 3600, 1),
            'subjects': subjects_data
        })
        
    return render(request, 'analytics_dashboard.html', {'analytics_data': analytics_data})


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
    # Deprecated by setup_api_key, but keeping route to redirect
    return redirect('setup_api_key')

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
    # type param ignored, always content
    file_path = note.get_file_path()
        
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'))
    return HttpResponse("")

@login_required
def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, exam__user=request.user)
    
    # Optimize: Fetch all videos once, calculate stats in python
    videos = list(subject.videos.all().prefetch_related('chunks')) 
    
    total_items = 0
    completed_items = 0
    
    for v in videos:
        if v.is_chunked:
            chunks = v.chunks.all()
            total_items += len(chunks)
            completed_items += sum(1 for c in chunks if c.is_watched)
        else:
            total_items += 1
            if v.is_watched:
                completed_items += 1
                
    note, created = Note.objects.get_or_create(subject=subject)
    # CONTENT LOAD REMOVED - Handled by lazy loading via get_note_content
    
    progress = (completed_items / total_items * 360) if total_items > 0 else 0
    
    # Daily Progress
    today = timezone.localdate()
    daily_log, _ = DailyStudyLog.objects.get_or_create(user=request.user, subject=subject, date=today)
    today_minutes = round(daily_log.seconds_watched / 60, 1)
    
    # Playlist Stats (Hours)
    total_seconds_watched = 0
    total_seconds_left = 0
    
    for v in videos:
        if v.is_chunked:
            # For chunked, we calculate based on watched chunks
             # This is tricky without exact chunk duration if slightly uneven, but valid enough
             for c in v.chunks.all():
                 dur = c.end_seconds - c.start_seconds
                 if c.is_watched:
                     total_seconds_watched += dur
                 else:
                     total_seconds_left += dur
        else:
            if v.is_watched:
                total_seconds_watched += v.duration_seconds
            else:
                total_seconds_left += v.duration_seconds

    
    watched_hours = "{:.2f}".format(total_seconds_watched / 3600)
    left_hours = "{:.2f}".format(total_seconds_left / 3600)

    return render(request, 'subject_detail.html', {
        'subject': subject,
        'videos': videos,
        'note': note,
        'progress': progress,
        'total': total_items,
        'completed': completed_items,
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
        
        # Enforce API Key
        api_key = request.user.profile.google_api_key
        if not api_key:
            return redirect('setup_api_key')
            
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
            messages.success(request, f"Successfully added {len(videos_data)} videos from playlist.")
        else:
            messages.error(request, 'Failed to fetch playlist items. Please check the URL and your API Key.')

    return redirect('subject_detail', subject_id=subject.id)

@login_required
def add_video(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, exam__user=request.user)
    if request.method == 'POST':
        url = request.POST.get('video_url')
        mode = request.POST.get('mode', 'whole') # 'whole' or 'chunk'
        
        # Enforce API Key
        api_key = request.user.profile.google_api_key
        if not api_key: return redirect('setup_api_key')
        
        details = fetch_video_details(url, api_key)
        if not details:
             # Handle error
             return redirect('subject_detail', subject_id=subject.id)
             
        # Determine Order
        existing_count = Video.objects.filter(subject=subject).count()
        
        video = Video.objects.create(
            subject=subject,
            title=details['title'],
            video_id=details['video_id'],
            url=details['url'],
            order=existing_count,
            duration_seconds=details['duration'],
            is_chunked=(mode == 'chunk')
        )
        
        if mode == 'chunk':
            try:
                interval_mins = int(request.POST.get('interval', 20))
            except: interval_mins = 20
            
            interval_seconds = interval_mins * 60
            duration = details['duration']
            
            chunks = []
            start = 0
            part = 1
            while start < duration:
                end = min(start + interval_seconds, duration)
                
                # Title
                # Convert seconds to MM:SS
                def fmt(s): return f"{s//60:02d}:{s%60:02d}"
                chunk_title = f"Part {part} ({fmt(start)} - {fmt(end)})"
                
                chunks.append(VideoChunk(
                    video=video,
                    part_number=part,
                    title=chunk_title,
                    start_seconds=start,
                    end_seconds=end
                ))
                
                start = end
                part += 1
            
            VideoChunk.objects.bulk_create(chunks)
            
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
    today = timezone.localdate()
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

    # Update Global Daily Goal from Video Watch Time
    # If video is watched, we add the duration to the *Global* Daily Goal progress
    # NOTE: This assumes `DailyGoal` tracks TOTAL study time, including videos.
    # If `DailyGoal` is only for "Focus Timer", then we shouldn't add this.
    # BUT, usually users want *all* study time to count.
    # Let's add video duration to DailyGoal if it exists.
    daily_goal = DailyGoal.objects.filter(user=request.user, date=today).first()
    if daily_goal and video.is_watched:
         daily_goal.completed_seconds += video.duration_seconds
         # Check Goal
         goal_seconds = int(daily_goal.goal_hours * 3600)
         if daily_goal.completed_seconds >= goal_seconds and not daily_goal.achieved:
            daily_goal.achieved = True
            profile = request.user.profile
            streak, _ = Streak.objects.get_or_create(user=request.user)
            profile.current_streak += 1
            profile.last_goal_date = today
            profile.save()
            streak.current_streak = profile.current_streak
            streak.best_streak = max(streak.best_streak, streak.current_streak)
            streak.save()
         daily_goal.save()
    elif daily_goal and not video.is_watched: # Unchecking
         daily_goal.completed_seconds = max(0, daily_goal.completed_seconds - video.duration_seconds)
         daily_goal.save()

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
def update_chunk_status(request, chunk_id):
    chunk = get_object_or_404(VideoChunk, id=chunk_id, video__subject__exam__user=request.user)
    import json
    data = json.loads(request.body)
    chunk.is_watched = data.get('is_watched', False)
    chunk.save()
    
    # Update Daily Log
    today = timezone.localdate()
    daily_log, _ = DailyStudyLog.objects.get_or_create(
        user=request.user, 
        subject=chunk.video.subject, 
        date=today
    )
    
    duration = chunk.end_seconds - chunk.start_seconds
    if chunk.is_watched:
        daily_log.seconds_watched += duration
    else:
        daily_log.seconds_watched = max(0, daily_log.seconds_watched - duration)
        
    daily_log.save()
    today_minutes = round(daily_log.seconds_watched / 60, 1)

    # Update Global Goal for Chunk
    daily_goal = DailyGoal.objects.filter(user=request.user, date=today).first()
    if daily_goal:
        if chunk.is_watched:
             daily_goal.completed_seconds += duration
             goal_seconds = int(daily_goal.goal_hours * 3600)
             if daily_goal.completed_seconds >= goal_seconds and not daily_goal.achieved:
                daily_goal.achieved = True
                profile = request.user.profile
                streak, _ = Streak.objects.get_or_create(user=request.user)
                profile.current_streak += 1
                profile.last_goal_date = today
                profile.save()
                streak.current_streak = profile.current_streak
                streak.best_streak = max(streak.best_streak, streak.current_streak)
                streak.save()
        else:
             daily_goal.completed_seconds = max(0, daily_goal.completed_seconds - duration)
        daily_goal.save()
    
    return JsonResponse({
        'status': 'ok',
        'today_minutes': today_minutes
    })

@require_POST
@login_required
def save_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, subject__exam__user=request.user)
    import json
    data = json.loads(request.body)
    # note_type = data.get('note_type', 'content') # Removed screenshot support
    
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
    today = timezone.localdate()
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
    
    today = timezone.localdate()
    daily_goal = DailyGoal.objects.filter(user=request.user, date=today).first()
    
    if not daily_goal:
        return JsonResponse({'status': 'error', 'message': 'No goal found'})
        
    daily_goal.completed_seconds += new_seconds
    
    # Check completion
    goal_seconds = int(daily_goal.goal_hours * 3600)
    if daily_goal.completed_seconds >= goal_seconds: # Check if met
        if not daily_goal.achieved: # First time met today
            daily_goal.achieved = True
            
            # Update Streak
            profile = request.user.profile
            streak, _ = Streak.objects.get_or_create(user=request.user)
            
            profile.current_streak += 1
            profile.last_goal_date = today
            profile.save()
            
            streak.current_streak = profile.current_streak
            streak.best_streak = max(streak.best_streak, streak.current_streak)
            streak.save()
            
        daily_goal.is_completed = True
        
        # Streak logic is handled above by checking if it wasn't achieved yet
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
    subject = get_object_or_404(Subject, id=subject_id, exam__user=request.user)
    try:
        count, _ = subject.videos.all().delete()
        messages.success(request, f"Successfully deleted {count} videos from playlist.")
    except Exception as e:
        messages.error(request, f"Error deleting playlist: {e}")
    return redirect('subject_detail', subject_id=subject.id)

@require_POST
@login_required
def upload_csv_todo(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, exam__user=request.user)
    
    if 'file' not in request.FILES:
        return JsonResponse({'success': False, 'message': 'No file uploaded'})
        
    file = request.FILES['file']
    
    if not file.name.endswith('.csv'):
        return JsonResponse({'success': False, 'message': 'Invalid file type. Please upload a CSV file.'})
        
    try:
        from core.services.csv_importer import import_videos_from_csv
        # Read file content safely
        file_data = file.read().decode('utf-8')
        
        result = import_videos_from_csv(file_data, subject)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_POST
@login_required
def set_global_goal(request):
    import json
    data = json.loads(request.body)
    hours = float(data.get('hours', 0))
    today = timezone.localdate()
    
    obj, created = DailyGoal.objects.get_or_create(user=request.user, date=today, defaults={'goal_hours': hours})
    if not created:
        return JsonResponse({'status': 'exists', 'message': 'Goal already set for today!'})
        
    return JsonResponse({'status': 'ok'})

@require_POST
@login_required
def update_goal_status(request):
    return JsonResponse({'status': 'not_implemented'})

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


