#!/usr/bin/env bash
set -o errexit

pip3 install -r requirements.txt
python3 manage.py collectstatic --no-input
python3 manage.py migrate

python3 manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123');
    print('Superuser created')
else:
    print('Superuser already exists')
"