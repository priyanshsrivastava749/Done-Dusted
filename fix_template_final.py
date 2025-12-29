import os
import re

file_path = 'templates/subject_detail.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

original_content = content

# Fix 1: Daily Goal
# Pattern: <strong>Goal:</strong> {{ \n daily_goal }}m
# We use regex to be safe about whitespace
pattern1 = r'(<strong>Goal:</strong>\s*\{\{)\s*\n\s*(daily_goal\s*\}\}m)'
replacement1 = r'\1 \2'
content = re.sub(pattern1, r'<strong>Goal:</strong> {{ daily_goal }}m', content)

# Fix 2: Checkbox
# Pattern: {% if video.is_watched \n %}checked{% endif %}
pattern2 = r'(\{% if video\.is_watched)\s*\n\s*(%\}\s*checked\s*\{% endif %\}>)'
content = re.sub(pattern2, r'\1 \2', content)

# Fix 3: JS Escape
if '{{ subject.name|escapejs }}' not in content:
    content = content.replace(
        "printWindow.document.write('<h1>{{ subject.name }} Notes (' +",
        "printWindow.document.write('<h1>{{ subject.name|escapejs }} Notes (' +"
    )

if content != original_content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed template successfully.")
else:
    print("No changes made. Patterns might not have matched.")
    # Debug information
    match1 = re.search(pattern1, original_content)
    print(f"Match 1 found: {bool(match1)}")
    match2 = re.search(pattern2, original_content)
    print(f"Match 2 found: {bool(match2)}")
