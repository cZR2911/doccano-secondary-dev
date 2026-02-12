import sys
import os
import django

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from django.conf import settings
from django.urls import get_resolver

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

def list_urls(lis, acc=None):
    if acc is None:
        acc = []
    if not lis:
        return
    for l in lis:
        if hasattr(l, 'url_patterns'):
            list_urls(l.url_patterns, acc + [str(l.pattern)])
        else:
            print(''.join(acc) + str(l.pattern))

resolver = get_resolver()
list_urls(resolver.url_patterns)
