from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User, Group
from education.models import Student, Teacher, Course, Review
from education.roles import get_user_role
from django.db.models import Count, Avg
from .forms import (
    UserRegistrationForm, UserLoginForm, 
    UserProfileForm, StudentProfileForm, TeacherProfileForm
)


def register_view(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('education-home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.first_name}!')
            
            # Перенаправляем в зависимости от роли
            if user.groups.filter(name='Преподаватели').exists():
                return redirect('teacher-dashboard')
            else:
                return redirect('student-dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form, 'title': 'Регистрация'})


def login_view(request):
    """Вход в систему"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'С возвращением, {user.first_name}!')
            return redirect('dashboard')
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form, 'title': 'Вход'})


def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('education-home')


# ===== Проверки ролей =====
def is_admin(user):
    return user.is_authenticated and (
        user.is_superuser or 
        user.groups.filter(name='Администраторы').exists()
    )

def is_teacher(user):
    return user.is_authenticated and user.groups.filter(name='Преподаватели').exists()

def is_student(user):
    return user.is_authenticated and user.groups.filter(name='Студенты').exists()

def is_marketer(user):
    return user.is_authenticated and user.groups.filter(name='Маркетологи').exists()


# ===== Дашборды =====
@login_required
def profile_view(request):
    """Профиль пользователя"""
    user = request.user
    user_role = get_user_role(user)
    
    context = {
        'title': 'Мой профиль',
        'user': user,
        'user_role': user_role,
    }
    
    if hasattr(user, 'student_profile'):
        context['profile'] = user.student_profile
        context['profile_type'] = 'student'
    elif hasattr(user, 'teacher_profile'):
        context['profile'] = user.teacher_profile
        context['profile_type'] = 'teacher'
    
    return render(request, 'users/profile.html', context)


@login_required
def dashboard_redirect(request):
    """Перенаправление на соответствующий дашборд в зависимости от роли"""
    user = request.user
    
    if user.is_superuser or user.groups.filter(name='Администраторы').exists():
        return redirect('admin:index')
    elif user.groups.filter(name='Преподаватели').exists():
        return redirect('teacher-dashboard')
    elif user.groups.filter(name='Студенты').exists():
        return redirect('student-dashboard')
    elif user.groups.filter(name='Маркетологи').exists():
        return redirect('marketer-dashboard')
    else:
        messages.warning(request, 'У вас не назначена роль. Обратитесь к администратору.')
        return redirect('profile')


@login_required
def student_dashboard(request):
    """Личный кабинет студента"""
    user = request.user
    
    if not hasattr(user, 'student_profile'):
        messages.error(request, 'Профиль студента не найден')
        return redirect('education-home')
    
    student = user.student_profile
    enrollments = student.enrollments.select_related('group__course').all()
    
    context = {
        'title': 'Личный кабинет студента',
        'student': student,
        'enrollments': enrollments,
    }
    return render(request, 'users/student_dashboard.html', context)


@login_required
def teacher_dashboard(request):
    """Личный кабинет преподавателя"""
    user = request.user
    
    if not hasattr(user, 'teacher_profile'):
        messages.error(request, 'Профиль преподавателя не найден')
        return redirect('education-home')
    
    teacher = user.teacher_profile
    groups = teacher.groups.filter(is_active=True).select_related('course')
    
    context = {
        'title': 'Личный кабинет преподавателя',
        'teacher': teacher,
        'groups': groups,
    }
    return render(request, 'users/teacher_dashboard.html', context)


@login_required
def marketer_dashboard(request):
    """Личный кабинет маркетолога"""
    # Статистика для маркетолога
    published_courses = Course.published.count()
    draft_courses = Course.objects.filter(status=Course.Status.DRAFT).count()
    
    # Отзывы на модерации
    pending_reviews = Review.objects.filter(is_approved=False).count()
    
    # Популярные курсы
    popular_courses = Course.published.annotate(
        enrollment_count=Count('groups__enrollments'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-enrollment_count')[:5]
    
    # Последние отзывы
    recent_reviews = Review.objects.all().select_related('student', 'course').order_by('-review_date')[:10]
    
    context = {
        'title': 'Панель маркетолога',
        'published_courses': published_courses,
        'draft_courses': draft_courses,
        'pending_reviews': pending_reviews,
        'popular_courses': popular_courses,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'users/marketer_dashboard.html', context)


@login_required
def edit_profile(request):
    """Редактирование профиля"""
    user = request.user
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=user)
        
        if hasattr(user, 'student_profile'):
            profile = user.student_profile
            profile_form = StudentProfileForm(request.POST, instance=profile)
        elif hasattr(user, 'teacher_profile'):
            profile = user.teacher_profile
            profile_form = TeacherProfileForm(request.POST, request.FILES, instance=profile)
        else:
            profile_form = None
        
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        user_form = UserProfileForm(instance=user)
        
        if hasattr(user, 'student_profile'):
            profile_form = StudentProfileForm(instance=user.student_profile)
        elif hasattr(user, 'teacher_profile'):
            profile_form = TeacherProfileForm(instance=user.teacher_profile)
        else:
            profile_form = None
    
    context = {
        'title': 'Редактирование профиля',
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/edit_profile.html', context)