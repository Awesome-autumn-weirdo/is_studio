# education/admin.py
from django.contrib import admin
from .models import (
    Teacher, Course, Category, Group, Student, Enrollment, 
    Schedule, Attendance, Performance, Review, Administrator
)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'specialization', 'phone', 'is_active')
    list_display_links = ('id', 'last_name')
    search_fields = ('last_name', 'first_name', 'specialization')
    list_filter = ('specialization', 'is_active')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'duration_hours', 'price', 'status', 'time_create')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'description')
    list_filter = ('status', 'category')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'course', 'teacher', 'format', 'start_date', 'end_date', 'is_active')
    list_display_links = ('id', 'name')
    list_filter = ('format', 'is_active', 'course')
    search_fields = ('name', 'course__title', 'teacher__last_name')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'email', 'phone', 'time_create')
    list_display_links = ('id', 'last_name')
    search_fields = ('last_name', 'first_name', 'email', 'phone')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'group', 'enrollment_date', 'is_active')
    list_display_links = ('id',)
    search_fields = ('student__last_name', 'group__course__title')
    list_filter = ('is_active', 'enrollment_date')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'date', 'time', 'classroom', 'topic')
    list_display_links = ('id',)
    list_filter = ('date', 'group__course')
    search_fields = ('group__course__title', 'classroom', 'topic')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'schedule', 'student', 'status')
    list_display_links = ('id',)
    list_filter = ('status', 'schedule__date')
    search_fields = ('student__last_name',)


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    # Исправлено: убрали 'group', добавили 'schedule'
    list_display = ('id', 'student', 'schedule', 'grade', 'created_at')
    list_display_links = ('id',)
    list_filter = ('grade', 'schedule__date', 'schedule__group__course')
    search_fields = ('student__last_name', 'schedule__group__course__title')
    ordering = ('-schedule__date',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course', 'rating', 'review_date', 'is_approved')
    list_display_links = ('id',)
    list_filter = ('rating', 'is_approved', 'course')
    search_fields = ('student__last_name', 'course__title', 'comment')
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'Одобрено {queryset.count()} отзывов')
    approve_reviews.short_description = 'Одобрить выбранные отзывы'


@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'position', 'phone')
    list_display_links = ('id', 'last_name')
    search_fields = ('last_name', 'first_name', 'position')