from django.urls import path
from . import views

urlpatterns = [
    # Главная страница
    path('', views.index, name='education-home'),
    
    # Курсы
    path('courses/', views.courses_list, name='courses-list'),
    path('courses/filter/', views.courses_filtered, name='courses-filtered'),
    path('course/create/', views.course_create, name='course-create'),
    path('course/<slug:course_slug>/', views.course_detail_slug, name='course-detail-slug'),
    path('course/<slug:course_slug>/update/', views.course_update, name='course-update'),
    path('course/<slug:course_slug>/delete/', views.course_delete, name='course-delete'),
    path('course/id/<int:course_id>/', views.course_detail, name='course-detail-id'),
    
    # Категории
    path('categories/', views.categories, name='categories'),
    path('category/create/', views.category_create, name='category-create'),
    path('category/<slug:cat_slug>/', views.category_detail, name='category-detail'),
    path('category/<slug:cat_slug>/update/', views.category_update, name='category-update'),
    path('category/<slug:cat_slug>/delete/', views.category_delete, name='category-delete'),
    
    # Преподаватели
    path('teachers/', views.teachers_list, name='teachers-list'),
    path('teacher/create/', views.teacher_create, name='teacher-create'),
    path('teacher/<int:teacher_id>/', views.teacher_detail, name='teacher-detail'),
    path('teacher/<int:teacher_id>/update/', views.teacher_update, name='teacher-update'),
    path('teacher/<int:teacher_id>/delete/', views.teacher_delete, name='teacher-delete'),
    
    # Группы
    path('groups/', views.groups_list, name='groups-list'),
    path('group/create/', views.group_create, name='group-create'),
    path('group/<int:group_id>/', views.group_detail, name='group-detail'),
    path('group/<int:group_id>/update/', views.group_update, name='group-update'),
    path('group/<int:group_id>/delete/', views.group_delete, name='group-delete'),

    # Студенты
    path('students/', views.students_list, name='students-list'),
    path('student/register/', views.student_register, name='student-register'),
    path('student/<int:student_id>/', views.student_detail, name='student-detail'),

    # Расписание
    path('schedule/', views.schedule_list, name='schedule-list'),
    path('schedule/my/', views.my_schedule, name='my-schedule'),
    path('schedule/create/', views.schedule_create, name='schedule-create'),
    path('schedule/<int:schedule_id>/update/', views.schedule_update, name='schedule-update'),
    path('schedule/<int:schedule_id>/delete/', views.schedule_delete, name='schedule-delete'),
    path('schedule/group/<int:group_id>/', views.group_schedule_detail, name='group-schedule'),

    # Посещаемость
    path('attendance/mark/<int:schedule_id>/', views.attendance_mark, name='attendance-mark'),
    path('attendance/group/<int:group_id>/', views.attendance_group_report, name='attendance-group-report'),
    path('attendance/my/', views.student_attendance, name='student-attendance'),
    
    # Успеваемость
    path('performance/group/<int:group_id>/add/', views.performance_add, name='performance-add'),
    path('performance/group/<int:group_id>/student/<int:student_id>/', views.performance_single_add, name='performance-single-add'),
    path('performance/group/<int:group_id>/report/', views.performance_group_report, name='performance-group-report'),
    path('performance/my/', views.student_performance, name='student-performance'),
    
    # Записи на курсы
    path('enrollment/create/', views.enrollment_create, name='enrollment-create'),
    path('enrollment/<int:enrollment_id>/delete/', views.enrollment_delete, name='enrollment-delete'),
    
    # Отзывы
    path('reviews/', views.reviews_list, name='reviews-list'),
    path('review/create/', views.review_create, name='review-create'),
    
    # Статистика
    path('statistics/', views.statistics, name='statistics'),
    
    # О нас
    path('about/', views.about, name='about'),
]