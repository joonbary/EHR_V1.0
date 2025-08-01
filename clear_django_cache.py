#!/usr/bin/env python
import os
import sys
import shutil

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

import django
django.setup()

from django.core.cache import cache
from django.template import engines
from django.template.loaders.cached import Loader

print("[INFO] Clearing Django caches...")

# 1. 일반 캐시 클리어
try:
    cache.clear()
    print("[OK] Django cache cleared")
except Exception as e:
    print(f"[ERROR] Failed to clear cache: {e}")

# 2. 템플릿 로더 캐시 클리어
try:
    for engine in engines.all():
        if hasattr(engine, 'engine'):
            for loader in engine.engine.template_loaders:
                if hasattr(loader, 'reset'):
                    loader.reset()
                    print(f"[OK] Template loader cache reset: {loader}")
except Exception as e:
    print(f"[ERROR] Failed to clear template cache: {e}")

# 3. Python 캐시 디렉토리 삭제
cache_dirs = [
    '__pycache__',
    '.pyc',
]

for root, dirs, files in os.walk('.'):
    # __pycache__ 디렉토리 삭제
    if '__pycache__' in dirs:
        pycache_path = os.path.join(root, '__pycache__')
        try:
            shutil.rmtree(pycache_path)
            print(f"[OK] Removed: {pycache_path}")
        except Exception as e:
            print(f"[ERROR] Failed to remove {pycache_path}: {e}")
    
    # .pyc 파일 삭제
    for file in files:
        if file.endswith('.pyc'):
            pyc_path = os.path.join(root, file)
            try:
                os.remove(pyc_path)
                print(f"[OK] Removed: {pyc_path}")
            except Exception as e:
                print(f"[ERROR] Failed to remove {pyc_path}: {e}")

print("\n[INFO] Cache clearing completed!")
print("[INFO] Please restart the Django server now.")