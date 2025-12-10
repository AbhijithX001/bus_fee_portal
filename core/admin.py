from django.contrib import admin
from .models import User, StudentProfile, FeeRecord


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'student_class', 'bus_route', 'monthly_fee']
    list_filter = ['student_class']
    search_fields = ['full_name']


@admin.register(FeeRecord)
class FeeRecordAdmin(admin.ModelAdmin):
    list_display = ['student_profile', 'month', 'status']
    list_filter = ['month', 'status']
    search_fields = ['student_profile__full_name']
    ordering = ['month']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'role', 'is_active']
    list_filter = ['role']
    search_fields = ['username']
