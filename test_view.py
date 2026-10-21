import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from studio.models import TeamMember, Project, Service, StudioPage
from studio.views import studio_home
from django.test import RequestFactory
import json
import re

factory = RequestFactory()
request = factory.get('/')
response = studio_home(request)

print('Response status:', response.status_code)
content = response.content.decode('utf-8')

# Check if proj element exists
if 'id="proj"' in content:
    print('[OK] Found id="proj" element')
else:
    print('[ERROR] Missing id="proj" element')

# Check if tm-grid element exists
if 'id="tm-grid"' in content:
    print('[OK] Found id="tm-grid" element')
else:
    print('[ERROR] Missing id="tm-grid" element')

# Find the studio-data script tag
match = re.search(r'<script id="studio-data" type="application/json">(.*?)</script>', content, re.DOTALL)
if match:
    print('[OK] Found studio-data script tag')
    print('Data length:', len(match.group(1)))
    data = json.loads(match.group(1))
    print('Keys:', list(data.keys()))
    print('\nTeam data:', data.get('team'))
    print('\nProjects data:', data.get('projects'))
    print('\nServices data:', data.get('services'))
else:
    print('[ERROR] No studio-data script tag found')
