import re

file_path = 'templates/subject_detail.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)

# Fix 1: Daily Goal
# Current: 
# <strong>Goal:</strong> {{
#                 daily_goal }}m
pattern1 = r'(<strong>Goal:</strong>\s*\{\{)\s*\n\s*(daily_goal\s*\}\}m)'
new_content = re.sub(pattern1, r'\1 \2', content)

if len(new_content) != len(content):
    print("Fix 1 applied.")
else:
    print("Fix 1 NOT applied. Regex mismatch.")

content = new_content

# Fix 2: Checkbox
# Current:
# <input type="checkbox" onchange="toggleWatched('{{ video.id }}', this)" {% if video.is_watched
#                         %}checked{% endif %}>
pattern2 = r'(type="checkbox"[^>]*\{% if video\.is_watched)\s*\n\s*(%\}\s*checked\s*\{% endif %\}>)'
new_content = re.sub(pattern2, r'\1 \2', content)

if len(new_content) != len(content):
    print("Fix 2 applied.")
else:
    print("Fix 2 NOT applied. Regex mismatch.")

if new_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("File saved.")
else:
    print("File not saved (no changes or only 1st fix applied?). Wait, check logic.")
    # Actually I updated content var, so asking if new_content != content checks 2nd fix.
    # To check overall:
    pass

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
