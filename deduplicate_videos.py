import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'done_dusted.settings')
django.setup()

from core.models import Subject, Video

subject = Subject.objects.get(name="GATE 2026")
print(f"Cleaning duplicates for {subject.name}...")

# Group by video_id (or title/url)
all_videos = list(subject.videos.all())
seen_video_ids = {}
to_delete = []

for video in all_videos:
    vid_id = video.video_id
    if vid_id not in seen_video_ids:
        seen_video_ids[vid_id] = video
    else:
        # If the current one is watched but the saved one isn't, swap them (keep the watched one)
        # Actually, if we are deleting, we should check if *any* of the duplicates are watched.
        existing = seen_video_ids[vid_id]
        if video.is_watched and not existing.is_watched:
            to_delete.append(existing)
            seen_video_ids[vid_id] = video
        else:
            to_delete.append(video)

# input("Press Enter to delete...")

# Delete in chunks
count = 0
for v in to_delete:
    v.delete()
    count += 1

print(f"Deleted {count} duplicates.")
print(f"Remaining videos: {subject.videos.count()}")
