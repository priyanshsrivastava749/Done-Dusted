import requests
from django.conf import settings

def fetch_playlist_items(playlist_url, api_key):
    """
    Fetches videos from a YouTube playlist URL.
    Returns a list of dicts: [{'title':, 'video_id':, 'url':}]
    """
    # Extract playlist ID from URL
    if "list=" not in playlist_url:
        return None
    
    playlist_id = playlist_url.split("list=")[1].split("&")[0]
    
    api_url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        'part': 'snippet',
        'maxResults': 50,
        'playlistId': playlist_id,
        'key': api_key
    }
    
    videos = []
    next_page_token = None
    
    import re
    def parse_duration(duration_str):
        """Parses ISO 8601 duration string to seconds."""
        match = re.match(
            r'PT((?P<hours>\d+)H)?((?P<minutes>\d+)M)?((?P<seconds>\d+)S)?',
            duration_str
        )
        if not match:
            return 0
        
        hours = int(match.group('hours') or 0)
        minutes = int(match.group('minutes') or 0)
        seconds = int(match.group('seconds') or 0)
        return hours * 3600 + minutes * 60 + seconds

    while True:
        if next_page_token:
            params['pageToken'] = next_page_token
            
        try:
            response = requests.get(api_url, params=params)
            data = response.json()
            
            if 'error' in data:
                print(f"YouTube API Error: {data['error']}")
                return None
                
            items = data.get('items', [])
            if not items:
                break

            # Collect video IDs for batch details fetch
            video_ids = []
            snippet_map = {}
            
            for item in items:
                snippet = item['snippet']
                video_id = snippet['resourceId']['videoId']
                title = snippet['title']
                
                # Filter out deleted/private videos
                if title == "Private video" or title == "Deleted video":
                    continue
                
                video_ids.append(video_id)
                snippet_map[video_id] = title

            # Fetch content details (duration)
            if video_ids:
                details_url = "https://www.googleapis.com/youtube/v3/videos"
                details_params = {
                    'part': 'contentDetails',
                    'id': ','.join(video_ids),
                    'key': api_key
                }
                details_resp = requests.get(details_url, params=details_params)
                details_data = details_resp.json()
                
                duration_map = {}
                for vid_item in details_data.get('items', []):
                     vid_id = vid_item['id']
                     duration_str = vid_item['contentDetails']['duration']
                     duration_map[vid_id] = parse_duration(duration_str)

                # Assemble final list
                for vid_id in video_ids:
                    videos.append({
                        'title': snippet_map[vid_id],
                        'video_id': vid_id,
                        'url': f"https://www.youtube.com/watch?v={vid_id}",
                        'duration': duration_map.get(vid_id, 0)
                    })
            
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break
                
        except Exception as e:
            print(f"Error fetching playlist: {e}")
            return None
            
    return videos

def fetch_video_details(video_url, api_key):
    """
    Fetches details for a single video.
    Returns dict: {'title':, 'video_id':, 'duration':}
    """
    import re
    # Extract Video ID
    # Supports: youtube.com/watch?v=ID, youtu.be/ID
    video_id = None
    if "youtube.com" in video_url:
        if "v=" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]
    elif "youtu.be" in video_url:
        video_id = video_url.split("/")[-1].split("?")[0]
        
    if not video_id:
        return None

    api_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        'part': 'snippet,contentDetails',
        'id': video_id,
        'key': api_key
    }
    
    try:
        response = requests.get(api_url, params=params)
        data = response.json()
        
        if 'items' not in data or not data['items']:
            return None
            
        item = data['items'][0]
        snippet = item['snippet']
        content_details = item['contentDetails']
        
        # Parse Duration
        def parse_duration(duration_str):
             match = re.match(
                r'PT((?P<hours>\d+)H)?((?P<minutes>\d+)M)?((?P<seconds>\d+)S)?',
                duration_str
            )
             if not match: return 0
             hours = int(match.group('hours') or 0)
             minutes = int(match.group('minutes') or 0)
             seconds = int(match.group('seconds') or 0)
             return hours * 3600 + minutes * 60 + seconds

        duration = parse_duration(content_details['duration'])
        
        return {
            'title': snippet['title'],
            'video_id': video_id,
            'duration': duration,
            'url': f"https://www.youtube.com/watch?v={video_id}"
        }
        
    except Exception as e:
        print(f"Error fetching video details: {e}")
        return None
