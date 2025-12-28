#!/usr/bin/env bash
set -o errexit

pip3 install -r requirements.txt
python3 manage.py collectstatic --no-input
python3 manage.py migrate

python3 manage.py shell -c "
from django.contrib.auth import get_user_model;
from core.models import StudentProfile, Bus;
User = get_user_model();

if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123');
    admin_user.role = 'admin';
    admin_user.save();
    print('Admin created with role');
else:
    admin = User.objects.get(username='admin');
    if admin.role != 'admin':
        admin.role = 'admin';
        admin.save();
        print('Admin role updated');
    else:
        print('Admin already exists');

if not Bus.objects.filter(bus_number=1).exists():
    test_bus = Bus.objects.create(
        bus_number=1,
        bus_name='Test Route A',
        driver_name='Test Driver',
        driver_phone='9876543210'
    );
    print('Test bus created');
else:
    test_bus = Bus.objects.get(bus_number=1);
    print('Test bus already exists');

if not User.objects.filter(username='test_student').exists():
    student_user = User.objects.create_user('test_student', password='password123');
    student_user.role = 'student';
    student_user.save();
    StudentProfile.objects.create(
        user=student_user,
        full_name='Test Student',
        student_class='10th Grade',
        bus=test_bus,
        bus_number=1,
        pickup_location='Test Location',
        bus_route='Test Route A',
        monthly_fee=500.00,
        parent_phone_number='1234567890',
        address='Test Address'
    );
    print('Test student created');
else:
    print('Test student already exists');
"