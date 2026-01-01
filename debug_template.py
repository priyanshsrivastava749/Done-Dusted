import os
import django
import sys
from django.conf import settings

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'done_dusted.settings')
django.setup()

from django.template import Template, Context

def check_chunk(content, chunk_name):
    try:
        Template(content)
        print(f"OK: {chunk_name}")
    except Exception as e:
        print(f"ERROR: {chunk_name} - {e}")

with open('templates/subject_detail.html', 'r', encoding='utf-8') as f:
    full_content = f.read()

# Split roughly
parts = full_content.split('{%')
print(f"Found {len(parts)} tags start")

# Check full first
check_chunk(full_content, "FULL FILE")
