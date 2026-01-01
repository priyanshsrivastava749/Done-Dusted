import re

with open('templates/subject_detail.html', 'r', encoding='utf-8') as f:
    content = f.read()

tags = re.findall(r'{%\s*(\w+)', content)
print(f"Found {len(tags)} tags:")
for i, tag in enumerate(tags):
    print(f"{i}: {tag}")
