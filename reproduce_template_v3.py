import os
import django
import sys
from django.conf import settings

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'done_dusted.settings')
django.setup()

from core.models import Subject, Note, Video
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.contrib.auth.models import User

try:
    s = Subject.objects.first()
    if not s:
        u = User.objects.first() or User.objects.create(username='temp')
        exam = u.exams.first() or u.exams.create(name='Test Exam')
        s = Subject.objects.create(name="Test Subject", exam=exam)

    note, _ = Note.objects.get_or_create(subject=s)
    
    # Mock request
    factory = RequestFactory()
    request = factory.get(f'/subject/{s.id}/')
    request.user = s.exam.user
    
    context = {
        'subject': s,
        'videos': s.videos.all(),
        'note': note,
        'progress': 50,
        'total': 10,
        'completed': 5,
        'today_minutes': 10,
        'daily_goal': 60,
        'remaining_goal': 50,
        'request': request, 
    }
    
    print(f"Rendering template for subject: {s.name}")
    rendered = render_to_string('subject_detail.html', context, request=request)
    print("Render successful.")
    
    for line in rendered.splitlines():
        if "Remaining:" in line:
            print(f"Found Remaining line: {line.strip()}")

except Exception as e:
    print(f"TEMPLATE ERROR CAUGHT: {e}")
    import traceback
    traceback.print_exc()
