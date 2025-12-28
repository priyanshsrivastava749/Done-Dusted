
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'done_dusted.settings')
django.setup()

from core.models import Video
print(f"Total Videos: {Video.objects.count()}")
for v in Video.objects.all()[:5]:
    print(f"ID: '{v.video_id}', Title: '{v.title}'")
