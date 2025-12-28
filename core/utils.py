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
    
    while True:
        if next_page_token:
            params['pageToken'] = next_page_token
            
        try:
            response = requests.get(api_url, params=params)
            data = response.json()
            
            if 'error' in data:
                print(f"YouTube API Error: {data['error']}")
                return None
                
            for item in data.get('items', []):
                snippet = item['snippet']
                video_id = snippet['resourceId']['videoId']
                title = snippet['title']
                
                # Filter out deleted/private videos usually having specific titles or no thumbnails
                if title == "Private video" or title == "Deleted video":
                    continue
                    
                videos.append({
                    'title': title,
                    'video_id': video_id,
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                })
            
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break
                
        except Exception as e:
            print(f"Error fetching playlist: {e}")
            return None
            
    return videos
