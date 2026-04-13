from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from .models import (
    Course, Category, Teacher, Student, Group, 
    Enrollment, Schedule, Attendance, Performance, Review
)
from datetime import date

class CourseForm(forms.ModelForm):
    """Форма для создания и редактирования курсов"""
    class Meta:
        model = Course
        fields = ['category', 'title', 'slug', 'description', 'full_description', 
                  'duration_hours', 'price', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'full_description': forms.Textarea(attrs={'rows': 5}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'category': 'Категория',
            'title': 'Название курса',
            'slug': 'URL-адрес',
            'description': 'Краткое описание',
            'full_description': 'Полное описание',
            'duration_hours': 'Длительность (часы)',
            'price': 'Стоимость (₽)',
            'status': 'Статус',
        }


class CategoryForm(forms.ModelForm):
    """Форма для создания и редактирования категорий"""
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': 'Название категории',
            'slug': 'URL-адрес',
            'description': 'Описание',
        }


class TeacherForm(forms.ModelForm):
    """Форма для создания и редактирования преподавателей"""
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'middle_name', 'specialization', 
                  'phone', 'email', 'bio', 'photo', 'is_active']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'middle_name': 'Отчество',
            'specialization': 'Специализация',
            'phone': 'Телефон',
            'email': 'Email',
            'bio': 'Биография',
            'photo': 'Фото',
            'is_active': 'Активен',
        }


class StudentForm(forms.ModelForm):
    """Форма для регистрации студентов"""
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'middle_name', 'phone', 
                  'email', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'middle_name': 'Отчество',
            'phone': 'Телефон',
            'email': 'Email',
            'birth_date': 'Дата рождения',
        }


class GroupForm(forms.ModelForm):
    """Форма для создания и редактирования групп"""
    class Meta:
        model = Group
        fields = ['course', 'teacher', 'name', 'start_date', 'end_date', 
                  'format', 'max_students', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'course': 'Курс',
            'teacher': 'Преподаватель',
            'name': 'Название группы',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'format': 'Формат обучения',
            'max_students': 'Макс. студентов',
            'is_active': 'Активна',
        }


class EnrollmentForm(forms.ModelForm):
    """Форма для записи студентов на курс"""
    class Meta:
        model = Enrollment
        fields = ['student', 'group']
        labels = {
            'student': 'Студент',
            'group': 'Группа',
        }


class ScheduleForm(forms.ModelForm):
    """Форма для создания расписания"""
    class Meta:
        model = Schedule
        fields = ['group', 'date', 'time', 'classroom', 'topic']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
        labels = {
            'group': 'Группа',
            'date': 'Дата занятия',
            'time': 'Время занятия',
            'classroom': 'Аудитория',
            'topic': 'Тема занятия',
        }


class AttendanceForm(forms.ModelForm):
    """Форма для отметки посещаемости"""
    class Meta:
        model = Attendance
        fields = ['student', 'status', 'note']
        labels = {
            'student': 'Студент',
            'status': 'Статус',
            'note': 'Примечание',
        }


class PerformanceForm(forms.ModelForm):
    """Форма для выставления оценок"""
    class Meta:
        model = Performance
        fields = ['student', 'grade', 'comment']
        labels = {
            'student': 'Студент',
            'grade': 'Оценка',
            'comment': 'Комментарий',
        }


class ReviewForm(forms.ModelForm):
    """Форма для создания отзыва"""
    class Meta:
        model = Review
        fields = ['course', 'rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'course': 'Курс',
            'rating': 'Оценка (1-5)',
            'comment': 'Комментарий',
        }


# Форма для фильтрации курсов
class CourseFilterForm(forms.Form):
    """Форма для фильтрации курсов"""
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='Категория',
        empty_label='Все категории'
    )
    status = forms.ChoiceField(
        choices=[('', 'Все статусы')] + Course.Status.choices,
        required=False,
        label='Статус'
    )
    price_min = forms.DecimalField(
        required=False,
        min_value=0,
        label='Цена от',
        widget=forms.NumberInput(attrs={'placeholder': '₽'})
    )
    price_max = forms.DecimalField(
        required=False,
        min_value=0,
        label='Цена до',
        widget=forms.NumberInput(attrs={'placeholder': '₽'})
    )
    search = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={'placeholder': 'Название курса...'})
    )
    ordering = forms.ChoiceField(
        choices=[
            ('title', 'По названию (А-Я)'),
            ('-title', 'По названию (Я-А)'),
            ('price', 'По цене (возрастание)'),
            ('-price', 'По цене (убывание)'),
            ('-time_create', 'Сначала новые'),
            ('time_create', 'Сначала старые'),
        ],
        required=False,
        label='Сортировка'
    )