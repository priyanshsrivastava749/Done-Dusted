import re

file_path = 'templates/subject_detail.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)

# Fix Checkbox Split
# Current:
# <input type="checkbox" onchange="toggleWatched('{{ video.id }}', this)" {% if video.is_watched
#                         %}checked{% endif %}>
# Regex needs to be flexible with whitespace
pattern = r'(type="checkbox"[^>]*\{% if video\.is_watched)\s*\n\s*(%\}\s*checked\s*\{% endif %\}>)'
new_content = re.sub(pattern, r'\1 \2', content)

if len(new_content) != len(content) or new_content != content:
    print("Fix applied.")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("File saved.")
else:
    print("Fix NOT applied. Regex mismatch.")
    # Debug: print snippet
    search_snip = "video.is_watched"
    idx = content.find(search_snip)
    if idx != -1:
        print(f"Found snippet context:\n{content[idx-50:idx+100]}")
