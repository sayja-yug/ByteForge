"""
Custom template filters for learning app
"""
from django import template
import re

register = template.Library()


@register.filter
def youtube_video_id(url):
    """
    Extract YouTube video ID from various YouTube URL formats
    
    Handles:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    """
    if not url:
        return None
    
    # Pattern for youtube.com/watch?v=
    pattern1 = r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern1, url)
    
    if match:
        return match.group(1)
    
    return None


@register.filter
def youtube_embed_url(url):
    """
    Convert any YouTube URL to embed format
    """
    video_id = youtube_video_id(url)
    if video_id:
        return f'https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1'
    return url
@register.filter
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary or list
    Usage: {{ my_dict|get_item:key }} or {{ my_list|get_item:index }}
    """
    try:
        if isinstance(dictionary, dict):
            return dictionary.get(str(key)) or dictionary.get(int(key)) or dictionary.get(key)
        elif isinstance(dictionary, list):
            return dictionary[int(key)]
        return None
    except (KeyError, IndexError, ValueError, TypeError):
        return None


@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
