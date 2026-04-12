from django.urls import path
from . import views

urlpatterns = [
    # Главная страница
    path('', views.index, name='education-home'),
    
    # Курсы
    path('courses/', views.courses_list, name='courses-list'),
    path('course/<slug:course_slug>/', views.course_detail_slug, name='course-detail-slug'),
    path('course/id/<int:course_id>/', views.course_detail, name='course-detail-id'),  # для обратной совместимости
    
    # Категории
    path('categories/', views.categories, name='categories'),
    path('category/<slug:cat_slug>/', views.category_detail, name='category-detail'),
    
    # Преподаватели
    path('teachers/', views.teachers_list, name='teachers-list'),
    path('teacher/<int:teacher_id>/', views.teacher_detail, name='teacher-detail'),
    
    # Отзывы
    path('reviews/', views.reviews_list, name='reviews-list'),
    
    # О нас
    path('about/', views.about, name='about'),
]