# education/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from .models import Course, Category, Teacher, Review, Student, Group, Enrollment
from django.db.models import Q, Count, Avg

# Главная страница
def index(request):
    # Получаем только опубликованные курсы
    published_courses = Course.published.all().select_related('category')[:6]
    
    # Популярные курсы (по количеству записей)
    popular_courses = Course.published.annotate(
        student_count=Count('groups__enrollments')
    ).order_by('-student_count')[:3]
    
    # Последние отзывы
    latest_reviews = Review.objects.filter(
        is_approved=True
    ).select_related('student', 'course')[:5]
    
    # Категории с количеством курсов
    categories = Category.objects.annotate(
        course_count=Count('courses', filter=Q(courses__status=Course.Status.PUBLISHED))
    ).filter(course_count__gt=0)
    
    data = {
        'title': 'Студия дополнительного образования',
        'courses': published_courses,
        'popular_courses': popular_courses,
        'latest_reviews': latest_reviews,
        'categories': categories,
    }
    return render(request, 'education/index.html', data)

# Список всех курсов
def courses_list(request):
    # Получаем все опубликованные курсы
    courses = Course.published.all().select_related('category').order_by('title')
    
    # Фильтрация по категории (если передан параметр)
    category_slug = request.GET.get('category')
    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    
    data = {
        'title': 'Все курсы',
        'courses': courses,
        'categories': Category.objects.all(),
    }
    return render(request, 'education/courses_list.html', data)

# Детальная страница курса
def course_detail_slug(request, course_slug):
    course = get_object_or_404(
        Course.objects.select_related('category').prefetch_related('groups__teacher'),
        slug=course_slug,
        status=Course.Status.PUBLISHED
    )
    
    # Получаем группы для этого курса
    groups = course.groups.filter(is_active=True)
    
    # Получаем отзывы о курсе
    reviews = course.reviews.filter(is_approved=True).select_related('student')
    
    # Средний рейтинг
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    
    data = {
        'title': course.title,
        'course': course,
        'groups': groups,
        'reviews': reviews,
        'avg_rating': avg_rating,
    }
    return render(request, 'education/course_detail.html', data)

# Страница с категориями
def categories(request):
    categories = Category.objects.annotate(
        course_count=Count('courses', filter=Q(courses__status=Course.Status.PUBLISHED))
    ).filter(course_count__gt=0)
    
    data = {
        'title': 'Категории курсов',
        'categories': categories,
    }
    return render(request, 'education/categories.html', data)

# Страница категории
def category_detail(request, cat_slug):
    category = get_object_or_404(Category, slug=cat_slug)
    courses = Course.published.filter(category=category).select_related('category')
    
    data = {
        'title': f'Курсы в категории "{category.name}"',
        'category': category,
        'courses': courses,
    }
    return render(request, 'education/category_detail.html', data)

# Страница со списком преподавателей
def teachers_list(request):
    teachers = Teacher.objects.filter(is_active=True).order_by('last_name')
    
    data = {
        'title': 'Наши преподаватели',
        'teachers': teachers,
    }
    return render(request, 'education/teachers_list.html', data)

# Детальная страница преподавателя
def teacher_detail(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id, is_active=True)
    groups = teacher.groups.filter(is_active=True).select_related('course')
    
    data = {
        'title': f'Преподаватель: {teacher.get_full_name()}',
        'teacher': teacher,
        'groups': groups,
    }
    return render(request, 'education/teacher_detail.html', data)

# Страница с отзывами
def reviews_list(request):
    reviews = Review.objects.filter(is_approved=True).select_related('student', 'course')
    
    data = {
        'title': 'Отзывы наших студентов',
        'reviews': reviews,
    }
    return render(request, 'education/reviews_list.html', data)

# Страница "О нас"
def about(request):
    data = {
        'title': 'О студии',
    }
    return render(request, 'education/about.html', data)

# Обработчик 404
def page_not_found(request, exception):
    return render(request, 'education/404.html', status=404)

# Перенаправление со старого адреса
def old_courses_redirect(request):
    return redirect('courses-list')

# ===== Устаревшие представления (можно удалить) =====
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, status=Course.Status.PUBLISHED)
    return redirect('course-detail-slug', course_slug=course.slug)