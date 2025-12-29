import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'done_dusted.settings')
django.setup()

from core.models import Subject, Video

for subject in Subject.objects.all():
    count = subject.videos.count()
    print(f"Subject: {subject.name}, Videos: {count}")
    # Check for duplicates
    videos = list(subject.videos.all())
    titles = [v.title for v in videos]
    if len(titles) != len(set(titles)):
        print(f"  WARNING: Duplicates found! Unique titles: {len(set(titles))}")
        # Print first few duplicates
        seen = set()
        dupes = []
        for x in titles:
            if x in seen:
                dupes.append(x)
            seen.add(x)
        print(f"  First 3 duplicates: {dupes[:3]}")
