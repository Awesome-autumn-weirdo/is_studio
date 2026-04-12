from django.contrib import admin
from .models import (
    Teacher, Course, Group, Student, Enrollment, 
    Schedule, Attendance, Performance, Review
)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'specialization', 'phone')
    list_display_links = ('id', 'last_name')
    search_fields = ('last_name', 'first_name', 'specialization')
    list_filter = ('specialization',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'duration_hours', 'price')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'description')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'teacher', 'format', 'start_date', 'end_date')
    list_display_links = ('id', 'course')
    list_filter = ('format', 'course')
    search_fields = ('course__title', 'teacher__last_name')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'email', 'phone', 'birth_date')
    list_display_links = ('id', 'last_name')
    search_fields = ('last_name', 'first_name', 'email', 'phone')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'group', 'enrollment_date')  # ← исправлено: enrollment_date вместо date_enrolled
    list_display_links = ('id',)
    search_fields = ('student__last_name', 'group__course__title')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'date', 'time', 'classroom')
    list_display_links = ('id',)
    list_filter = ('date', 'group__course')
    search_fields = ('group__course__title', 'classroom')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'schedule', 'student', 'status')
    list_display_links = ('id',)
    list_filter = ('status', 'schedule__date')
    search_fields = ('student__last_name',)


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'group', 'grade')
    list_display_links = ('id',)
    search_fields = ('student__last_name', 'group__course__title')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course', 'rating', 'review_date')
    list_display_links = ('id',)
    list_filter = ('rating', 'course')
    search_fields = ('student__last_name', 'course__title', 'comment')