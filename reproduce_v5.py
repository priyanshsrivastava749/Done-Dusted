import os
import django
import sys
from django.conf import settings

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'done_dusted.settings')
try:
    django.setup()
except Exception as e:
    with open('error_clean.txt', 'w', encoding='utf-8') as f:
        f.write(f"SETUP ERROR: {e}")
    sys.exit(1)

from core.models import Subject, Note
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

    print(f"Rendering template...")
    rendered = render_to_string('subject_detail.html', context, request=request)
    print("Render successful.")
    with open('error_clean.txt', 'w', encoding='utf-8') as f:
        f.write("SUCCESS")

except Exception as e:
    with open('error_clean.txt', 'w', encoding='utf-8') as f:
        f.write(str(e))
