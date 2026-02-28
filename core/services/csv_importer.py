import csv
import io
from django.db import models
from core.models import Video, Subject

import re

def parse_duration(duration_str):
    """
    Parses duration string (MM:SS, HH:MM:SS, "10 mins", "1.5 hours", "120") into seconds.
    Returns 0 if invalid.
    """
    duration_str = str(duration_str).strip().lower()
    if not duration_str:
        return 0
        
    if ':' in duration_str:
        parts = duration_str.split(':')
        try:
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        except ValueError:
            pass
            
    # Try to extract numbers
    # If it's just a number, assume minutes
    try:
        match = re.search(r'([\d\.]+)', duration_str)
        if match:
            val = float(match.group(1))
            if 'sec' in duration_str:
                return int(val)
            elif 'hr' in duration_str or 'hour' in duration_str:
                return int(val * 3600)
            else:
                return int(val * 60) # default to minutes
    except ValueError:
        pass
        
    return 0

def import_videos_from_csv(file, subject):
    """
    Parses a CSV file and creates Video objects for the given subject.
    Expects CSV with columns: title, duration
    Optional: description, youtube_link, video_id
    """
    # Ensure file is in text mode
    try:
        decoded_file = file.read().decode('utf-8-sig')
    except AttributeError:
         # Already string (e.g. from tests) or raw bytes needs decoding
         decoded_file = file if isinstance(file, str) else file.decode('utf-8-sig')
    
    io_string = io.StringIO(decoded_file)
    reader = csv.DictReader(io_string)
    
    # Normalize headers
    reader.fieldnames = [name.lower().strip() for name in reader.fieldnames]
    
    if 'title' not in reader.fieldnames:
        return {'success': False, 'message': 'Missing required column: title'}
        
    created_count = 0
    errors = []
    
    # Get current max order to append new videos
    current_max_order = subject.videos.aggregate(models.Max('order'))['order__max'] or 0
    next_order = current_max_order + 1

    for row_idx, row in enumerate(reader, start=1):
        title = row.get('title', '').strip()
        if not title:
            continue
            
        duration_str = row.get('duration', '00:00')
        duration_seconds = parse_duration(duration_str)
        
        # basic duplicate check via title?
        # For now, we allow duplicates as they might be different parts, 
        # or we could skip. Let's create for now.
        
        video_id = row.get('video_id', '')
        if not video_id:
             # Generate a dummy ID if not provided, as it's required by model
             import uuid
             video_id = f"csv-{uuid.uuid4().hex[:8]}"

        url = row.get('youtube_link', '')
        if not url:
            url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            Video.objects.create(
                subject=subject,
                title=title,
                duration_seconds=duration_seconds,
                video_id=video_id,
                url=url,
                order=next_order
            )
            next_order += 1
            created_count += 1
        except Exception as e:
            errors.append(f"Row {row_idx}: {str(e)}")

    return {
        'success': True,
        'items_created': created_count,
        'errors': errors
    }
