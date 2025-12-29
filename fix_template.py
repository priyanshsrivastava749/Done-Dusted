
import os

path = r"c:\Users\HP\Desktop\Done-Dusted\templates\subject_detail.html"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# The target split string
target = """                        <input type="checkbox" onchange="toggleWatched('{{ video.id }}', this)" {% if video.is_watched
                            %}checked{% endif %}>"""

# The replacement proper string
replacement = """                        <input type="checkbox" onchange="toggleWatched('{{ video.id }}', this)" {% if video.is_watched %}checked{% endif %}>"""

if target in content:
    new_content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully replaced content.")
else:
    print("Target content NOT found.")
    # Debug: print what we find around that area
    start_marker = "onchange=\"toggleWatched('{{ video.id }}', this)\""
    idx = content.find(start_marker)
    if idx != -1:
        print("Found context:")
        print(repr(content[idx:idx+200]))
