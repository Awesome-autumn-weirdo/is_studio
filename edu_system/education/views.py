from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.db.models import Q, Count, Avg
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.db.models import Q, Count, Avg, Min, Max, Sum
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings

from .models import (
    Course, Category, Teacher, Student, Group, 
    Enrollment, Schedule, Attendance, Performance, Review
)
from .forms import (
    CourseForm, CategoryForm, TeacherForm, StudentForm,
    GroupForm, EnrollmentForm, ScheduleForm, AttendanceForm,
    PerformanceForm, ReviewForm, CourseFilterForm
)
from .decorators import admin_required, teacher_required, student_required


def course_detail(request, course_id):
    """
    Перенаправление со старого URL с ID на новый URL со slug
    """
    course = get_object_or_404(Course, id=course_id, status=Course.Status.PUBLISHED)
    return redirect('course-detail-slug', course_slug=course.slug)

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

# ========== CRUD для курсов ==========

@login_required(login_url=settings.LOGIN_URL)
def course_create(request):
    """Создание нового курса"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Курс "{course.title}" успешно создан!')
            return redirect('course-detail-slug', course_slug=course.slug)
    else:
        form = CourseForm()
    
    data = {
        'title': 'Создание нового курса',
        'form': form,
    }
    return render(request, 'education/course_form.html', data)


@login_required(login_url=settings.LOGIN_URL)
def course_update(request, course_slug):
    """Редактирование курса"""
    course = get_object_or_404(Course, slug=course_slug)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Курс "{course.title}" успешно обновлен!')
            return redirect('course-detail-slug', course_slug=course.slug)
    else:
        form = CourseForm(instance=course)
    
    data = {
        'title': f'Редактирование курса: {course.title}',
        'form': form,
        'course': course,
    }
    return render(request, 'education/course_form.html', data)


@login_required(login_url=settings.LOGIN_URL)
def course_delete(request, course_slug):
    """Удаление курса"""
    course = get_object_or_404(Course, slug=course_slug)
    
    if request.method == 'POST':
        title = course.title
        course.delete()
        messages.success(request, f'Курс "{title}" успешно удален!')
        return redirect('courses-list')
    
    data = {
        'title': f'Удаление курса: {course.title}',
        'course': course,
    }
    return render(request, 'education/course_confirm_delete.html', data)


def courses_filtered(request):
    """Просмотр курсов с фильтрацией и сортировкой"""
    # Начинаем с опубликованных курсов
    courses = Course.published.all()
    
    # Создаем форму фильтрации
    form = CourseFilterForm(request.GET)
    
    if form.is_valid():
        # Фильтрация по категории
        category = form.cleaned_data.get('category')
        if category:
            courses = courses.filter(category=category)
        
        # Фильтрация по статусу
        status = form.cleaned_data.get('status')
        if status:
            courses = courses.filter(status=status)
        
        # Фильтрация по цене
        price_min = form.cleaned_data.get('price_min')
        if price_min:
            courses = courses.filter(price__gte=price_min)
        
        price_max = form.cleaned_data.get('price_max')
        if price_max:
            courses = courses.filter(price__lte=price_max)
        
        # Поиск по названию и описанию
        search = form.cleaned_data.get('search')
        if search:
            courses = courses.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Сортировка
        ordering = form.cleaned_data.get('ordering')
        if ordering:
            courses = courses.order_by(ordering)
        else:
            courses = courses.order_by('-time_create')
    
    # Добавляем связанные данные
    courses = courses.select_related('category')
    
    # Статистика
    stats = {
        'total': courses.count(),
        'avg_price': courses.aggregate(avg=Avg('price'))['avg'],
        'min_price': courses.aggregate(min=Min('price'))['min'],
        'max_price': courses.aggregate(max=Max('price'))['max'],
        'total_duration': courses.aggregate(sum=Sum('duration_hours'))['sum'],
    }
    
    data = {
        'title': 'Каталог курсов',
        'courses': courses,
        'form': form,
        'stats': stats,
    }
    return render(request, 'education/courses_filtered.html', data)


# ========== CRUD для категорий ==========

@login_required(login_url=settings.LOGIN_URL)
def category_create(request):
    """Создание новой категории"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Категория "{category.name}" успешно создана!')
            return redirect('categories')
    else:
        form = CategoryForm()
    
    data = {
        'title': 'Создание новой категории',
        'form': form,
    }
    return render(request, 'education/category_form.html', data)


@login_required(login_url=settings.LOGIN_URL)
def category_update(request, cat_slug):
    """Редактирование категории"""
    category = get_object_or_404(Category, slug=cat_slug)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Категория "{category.name}" успешно обновлена!')
            return redirect('categories')
    else:
        form = CategoryForm(instance=category)
    
    data = {
        'title': f'Редактирование категории: {category.name}',
        'form': form,
        'category': category,
    }
    return render(request, 'education/category_form.html', data)


@login_required(login_url=settings.LOGIN_URL)
def category_delete(request, cat_slug):
    """Удаление категории"""
    category = get_object_or_404(Category, slug=cat_slug)
    
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Категория "{name}" успешно удалена!')
        return redirect('categories')
    
    data = {
        'title': f'Удаление категории: {category.name}',
        'category': category,
    }
    return render(request, 'education/category_confirm_delete.html', data)


# ========== CRUD для студентов ==========

def student_register(request):
    """Регистрация нового студента"""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Студент {student.get_full_name()} успешно зарегистрирован!')
            return redirect('students-list')
    else:
        form = StudentForm()
    
    data = {
        'title': 'Регистрация студента',
        'form': form,
    }
    return render(request, 'education/student_form.html', data)


def students_list(request):
    """Список всех студентов"""
    students = Student.objects.all().order_by('last_name', 'first_name')
    
    # Статистика
    stats = {
        'total': students.count(),
        'active': students.filter(enrollments__is_active=True).distinct().count(),
    }
    
    data = {
        'title': 'Список студентов',
        'students': students,
        'stats': stats,
    }
    return render(request, 'education/students_list.html', data)


@login_required(login_url=settings.LOGIN_URL)
def student_detail(request, student_id):
    """Информация о студенте"""
    student = get_object_or_404(Student, id=student_id)
    
    # Записи на курсы
    enrollments = student.enrollments.select_related('group__course').all()
    
    # Посещаемость
    attendance = student.attendance.select_related('schedule__group__course').all()[:10]
    
    # Успеваемость
    performance = student.performance.select_related('group__course').all()
    
    # Отзывы
    reviews = student.reviews.select_related('course').all()
    
    data = {
        'title': f'Студент: {student.get_full_name()}',
        'student': student,
        'enrollments': enrollments,
        'attendance': attendance,
        'performance': performance,
        'reviews': reviews,
    }
    return render(request, 'education/student_detail.html', data)


# ========== CRUD для преподавателей ==========

@login_required(login_url=settings.LOGIN_URL)
def teacher_create(request):
    """Добавление нового преподавателя"""
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f'Преподаватель {teacher.get_full_name()} успешно добавлен!')
            return redirect('teachers-list')
    else:
        form = TeacherForm()
    
    data = {
        'title': 'Добавление преподавателя',
        'form': form,
    }
    return render(request, 'education/teacher_form.html', data)


@login_required(login_url=settings.LOGIN_URL)
def teacher_update(request, teacher_id):
    """Редактирование преподавателя"""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, f'Данные преподавателя {teacher.get_full_name()} обновлены!')
            return redirect('teacher-detail', teacher_id=teacher.id)
    else:
        form = TeacherForm(instance=teacher)
    
    data = {
        'title': f'Редактирование: {teacher.get_full_name()}',
        'form': form,
        'teacher': teacher,
    }
    return render(request, 'education/teacher_form.html', data)


@login_required(login_url=settings.LOGIN_URL)
def teacher_delete(request, teacher_id):
    """Удаление преподавателя"""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        name = teacher.get_full_name()
        teacher.delete()
        messages.success(request, f'Преподаватель {name} удален!')
        return redirect('teachers-list')
    
    data = {
        'title': f'Удаление преподавателя: {teacher.get_full_name()}',
        'teacher': teacher,
    }
    return render(request, 'education/teacher_confirm_delete.html', data)

# ========== Группы ==========

@login_required(login_url=settings.LOGIN_URL)
def group_create(request):
    """Создание новой группы"""
    initial = {}
    course_id = request.GET.get('course')
    if course_id:
        try:
            initial['course'] = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'Группа "{group.name}" успешно создана!')
            return redirect('course-detail-slug', course_slug=group.course.slug)
    else:
        form = GroupForm(initial=initial)
    
    data = {
        'title': 'Создание новой группы',
        'form': form,
    }
    return render(request, 'education/group_form.html', data)


@login_required(login_url=settings.LOGIN_URL)
def group_update(request, group_id):
    """Редактирование группы"""
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, f'Группа "{group.name}" успешно обновлена!')
            return redirect('course-detail-slug', course_slug=group.course.slug)
    else:
        form = GroupForm(instance=group)
    
    data = {
        'title': f'Редактирование группы: {group.name}',
        'form': form,
        'group': group,
    }
    return render(request, 'education/group_form.html', data)


@login_required(login_url=settings.LOGIN_URL)
def group_delete(request, group_id):
    """Удаление группы"""
    group = get_object_or_404(Group, id=group_id)
    course_slug = group.course.slug
    
    if request.method == 'POST':
        name = group.name
        group.delete()
        messages.success(request, f'Группа "{name}" успешно удалена!')
        return redirect('course-detail-slug', course_slug=course_slug)
    
    data = {
        'title': f'Удаление группы: {group.name}',
        'group': group,
    }
    return render(request, 'education/group_confirm_delete.html', data)


def groups_list(request):
    """Список всех групп"""
    groups = Group.objects.select_related('course', 'teacher').all().order_by('-start_date')
    
    # Статистика
    active_groups = groups.filter(is_active=True)
    
    data = {
        'title': 'Список групп',
        'groups': groups,
        'active_count': active_groups.count(),
        'total_count': groups.count(),
    }
    return render(request, 'education/groups_list.html', data)


@login_required(login_url=settings.LOGIN_URL)
def group_detail(request, group_id):
    """Детальная информация о группе"""
    group = get_object_or_404(Group.objects.select_related('course', 'teacher'), id=group_id)
    
    # Студенты в группе
    enrollments = group.enrollments.select_related('student').all()
    
    # Расписание группы
    schedule = group.schedule.all().order_by('date', 'time')
    
    # Успеваемость студентов группы
    performance = group.performance.select_related('student').all()
    
    data = {
        'title': f'Группа: {group.name}',
        'group': group,
        'enrollments': enrollments,
        'schedule': schedule,
        'performance': performance,
    }
    return render(request, 'education/group_detail.html', data)


# ========== Запись на курсы ==========

@login_required(login_url=settings.LOGIN_URL)
def enrollment_create(request):
    """Запись студента на курс"""
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            messages.success(request, 
                f'Студент {enrollment.student.get_full_name()} записан в группу {enrollment.group.name}!')
            return redirect('student-detail', student_id=enrollment.student.id)
    else:
        # Предзаполнение формы
        initial = {}
        student_id = request.GET.get('student')
        group_id = request.GET.get('group')
        
        if student_id:
            try:
                initial['student'] = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                pass
        
        if group_id:
            try:
                initial['group'] = Group.objects.get(id=group_id)
            except Group.DoesNotExist:
                pass
        
        form = EnrollmentForm(initial=initial)
    
    data = {
        'title': 'Запись на курс',
        'form': form,
    }
    return render(request, 'education/enrollment_form.html', data)


@login_required(login_url=settings.LOGIN_URL)
def enrollment_delete(request, enrollment_id):
    """Отмена записи на курс"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    student_id = enrollment.student.id
    
    if request.method == 'POST':
        student_name = enrollment.student.get_full_name()
        group_name = enrollment.group.name
        enrollment.delete()
        messages.success(request, f'Запись студента {student_name} из группы {group_name} отменена!')
        return redirect('student-detail', student_id=student_id)
    
    data = {
        'title': 'Отмена записи',
        'enrollment': enrollment,
    }
    return render(request, 'education/enrollment_confirm_delete.html', data)


# ========== Отзывы ==========

@login_required(login_url=settings.LOGIN_URL)
def review_create(request):
    """Создание отзыва"""
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            # Привязываем текущего пользователя-студента
            if hasattr(request.user, 'student_profile'):
                review.student = request.user.student_profile
            review.save()
            messages.success(request, 'Спасибо за ваш отзыв!')
            return redirect('course-detail-slug', course_slug=review.course.slug)
    else:
        form = ReviewForm()
    
    data = {
        'title': 'Оставить отзыв',
        'form': form,
    }
    return render(request, 'education/review_form.html', data)


# ========== Статистика и отчеты ==========

def statistics(request):
    """Страница со статистикой"""
    # Общая статистика
    stats = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.filter(is_active=True).count(),
        'total_courses': Course.published.count(),
        'total_groups': Group.objects.filter(is_active=True).count(),
        'total_enrollments': Enrollment.objects.filter(is_active=True).count(),
        'avg_course_price': Course.published.aggregate(avg=Avg('price'))['avg'],
        'total_reviews': Review.objects.filter(is_approved=True).count(),
        'avg_rating': Review.objects.filter(is_approved=True).aggregate(avg=Avg('rating'))['avg'],
    }
    
    # Популярные курсы
    popular_courses = Course.published.annotate(
        student_count=Count('groups__enrollments')
    ).order_by('-student_count')[:5]
    
    # Популярные категории
    popular_categories = Category.objects.annotate(
        course_count=Count('courses', filter=Q(courses__status=Course.Status.PUBLISHED))
    ).order_by('-course_count')[:5]
    
    # Активные преподаватели
    active_teachers = Teacher.objects.filter(is_active=True).annotate(
        group_count=Count('groups', filter=Q(groups__is_active=True))
    ).order_by('-group_count')[:5]
    
    data = {
        'title': 'Статистика',
        'stats': stats,
        'popular_courses': popular_courses,
        'popular_categories': popular_categories,
        'active_teachers': active_teachers,
    }
    return render(request, 'education/statistics.html', data)


    # ========== РАСПИСАНИЕ ==========

def schedule_list(request):
    """Просмотр общего расписания (доступно всем)"""
    # Фильтрация по группе, если указана
    group_id = request.GET.get('group')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    schedules = Schedule.objects.select_related('group__course', 'group__teacher').all()
    
    if group_id:
        schedules = schedules.filter(group_id=group_id)
    
    if date_from:
        schedules = schedules.filter(date__gte=date_from)
    
    if date_to:
        schedules = schedules.filter(date__lte=date_to)
    
    # Сортировка
    schedules = schedules.order_by('date', 'time')
    
    # Список групп для фильтра
    groups = Group.objects.filter(is_active=True).select_related('course')
    
    data = {
        'title': 'Расписание занятий',
        'schedules': schedules,
        'groups': groups,
        'selected_group': group_id,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'education/schedule_list.html', data)


@login_required
@admin_required
def schedule_create(request):
    """Создание нового занятия (только администратор)"""
    initial = {}
    group_id = request.GET.get('group')
    
    if group_id:
        try:
            initial['group'] = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save()
            messages.success(request, 
                f'Занятие для группы "{schedule.group.name}" добавлено в расписание!')
            return redirect('schedule-list')
    else:
        form = ScheduleForm(initial=initial)
    
    data = {
        'title': 'Добавление занятия в расписание',
        'form': form,
    }
    return render(request, 'education/schedule_form.html', data)


@login_required
@admin_required
def schedule_update(request, schedule_id):
    """Редактирование занятия (только администратор)"""
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Расписание успешно обновлено!')
            return redirect('schedule-list')
    else:
        form = ScheduleForm(instance=schedule)
    
    data = {
        'title': f'Редактирование занятия: {schedule.group.name}',
        'form': form,
        'schedule': schedule,
    }
    return render(request, 'education/schedule_form.html', data)


@login_required
@admin_required
def schedule_delete(request, schedule_id):
    """Удаление занятия (только администратор)"""
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    if request.method == 'POST':
        group_name = schedule.group.name
        date = schedule.date
        schedule.delete()
        messages.success(request, f'Занятие группы "{group_name}" на {date} удалено!')
        return redirect('schedule-list')
    
    data = {
        'title': 'Удаление занятия',
        'schedule': schedule,
    }
    return render(request, 'education/schedule_confirm_delete.html', data)


@login_required
def my_schedule(request):
    """Расписание для текущего пользователя"""
    user = request.user
    
    if hasattr(user, 'teacher_profile'):
        # Преподаватель видит расписание своих групп
        teacher = user.teacher_profile
        schedules = Schedule.objects.filter(
            group__teacher=teacher,
            group__is_active=True
        ).select_related('group__course').order_by('date', 'time')
        
        title = f'Моё расписание - {teacher.get_full_name()}'
        
    elif hasattr(user, 'student_profile'):
        # Студент видит расписание своих групп
        student = user.student_profile
        schedules = Schedule.objects.filter(
            group__enrollments__student=student,
            group__enrollments__is_active=True,
            group__is_active=True
        ).select_related('group__course', 'group__teacher').order_by('date', 'time')
        
        title = f'Моё расписание - {student.get_full_name()}'
        
    else:
        messages.warning(request, 'У вас нет привязанного профиля')
        return redirect('schedule-list')
    
    data = {
        'title': title,
        'schedules': schedules,
    }
    return render(request, 'education/my_schedule.html', data)


@login_required
@teacher_required
def group_schedule_detail(request, group_id):
    """Детальное расписание группы (для преподавателя)"""
    group = get_object_or_404(Group, id=group_id)
    
    # Проверяем, что преподаватель имеет доступ к этой группе
    if hasattr(request.user, 'teacher_profile'):
        teacher = request.user.teacher_profile
        if group.teacher != teacher and not request.user.is_superuser:
            messages.error(request, 'У вас нет доступа к расписанию этой группы')
            return redirect('teacher-dashboard')
    
    schedules = group.schedule.all().order_by('date', 'time')
    
    data = {
        'title': f'Расписание группы: {group.name}',
        'group': group,
        'schedules': schedules,
    }
    return render(request, 'education/group_schedule.html', data)