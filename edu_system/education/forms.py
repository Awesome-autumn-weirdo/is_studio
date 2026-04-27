import random
import string

from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from .models import (
    Course, Category, Teacher, Student, Group as EduGroup, 
    Enrollment, Schedule, Attendance, Performance, Review
)
from datetime import date
from django.contrib.auth.models import User, Group as AuthGroup
from django.core.exceptions import ValidationError



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
    """Форма для добавления преподавателя (с автосозданием пользователя)"""
    
    # Поля для создания пользователя
    username = forms.CharField(
        max_length=50,
        required=False,
        label='Логин',
        help_text='Оставьте пустым для автоматической генерации'
    )
    password = forms.CharField(
        max_length=50,
        required=False,
        label='Пароль',
        widget=forms.PasswordInput(),
        help_text='Оставьте пустым для автоматической генерации'
    )
    
    class Meta:
        model = Teacher
        fields = [
            'first_name', 'last_name', 'middle_name', 'specialization',
            'phone', 'email', 'bio', 'photo', 'is_active'
        ]
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
    
    def clean_email(self):
        """Проверка уникальности email"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            # Проверяем, не принадлежит ли email этому преподавателю
            if not self.instance.pk or self.instance.user.email != email:
                raise forms.ValidationError('Пользователь с таким email уже существует')
        return email
    
    def save(self, commit=True):
        teacher = super().save(commit=False)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        email = self.cleaned_data.get('email', '')
        
        if not username and teacher.last_name:
            username = self.generate_username(teacher.last_name)
        
        # Сохраняем сгенерированный пароль
        if not password:
            password = self.generate_password()
        
        # Сохраняем данные для входа в объекте формы
        self.generated_username = username
        self.generated_password = password
        
        if not email:
            email = f"{username}@studio.ru"
        
        # Создаем пользователя
        if teacher.user:
            user = teacher.user
            user.username = username
            user.email = email
            user.first_name = teacher.first_name
            user.last_name = teacher.last_name
            user.set_password(password)
            user.save()
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=teacher.first_name,
                last_name=teacher.last_name
            )
        
        teacher.user = user
        
        if commit:
            teacher.save()
            # Добавляем в группу
            teacher_group = AuthGroup.objects.get_or_create(name='Преподаватели')[0]
            user.groups.add(teacher_group)
        
        return teacher
    
    def generate_username(self, last_name):
        """Генерация уникального логина"""
        base = last_name.lower().replace(' ', '_')
        while True:
            suffix = ''.join(random.choices(string.digits, k=4))
            username = f"teacher_{base}_{suffix}"
            if not User.objects.filter(username=username).exists():
                return username
    
    def generate_password(self):
        """Генерация случайного пароля"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=12))

    def clean_photo(self):
                """Проверка размера фото в форме"""
                photo = self.cleaned_data.get('photo')
                
                if photo:
                    # Проверка размера (5 МБ)
                    if photo.size > 5 * 1024 * 1024:
                        raise ValidationError('Размер файла не должен превышать 5 МБ')
                    
                    # Проверка расширения
                    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
                    ext = str(photo.name).lower()
                    if not any(ext.endswith(ext_allowed) for ext_allowed in allowed_extensions):
                        raise ValidationError('Поддерживаются только форматы: JPG, PNG, GIF')
                
                return photo


class StudentForm(forms.ModelForm):
    """Форма для регистрации студента (с автосозданием пользователя)"""
    username = forms.CharField(
        max_length=50, required=False, label='Логин',
        help_text='Оставьте пустым для автоматической генерации'
    )
    password = forms.CharField(
        max_length=50, required=False, label='Пароль',
        widget=forms.PasswordInput(),
        help_text='Оставьте пустым для автоматической генерации'
    )
    
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email', 'birth_date']
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
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email
    
    def save(self, commit=True):
        student = super().save(commit=False)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if not username:
            username = self._generate_username(student.last_name)
        if not password:
            password = self._generate_password()
        
        # Сохраняем для отображения
        self.generated_username = username
        self.generated_password = password
        
        user = User.objects.create_user(
            username=username,
            email=student.email,
            password=password,
            first_name=student.first_name,
            last_name=student.last_name
        )
        
        student.user = user
        
        if commit:
            student.save()
            # Добавляем в группу
            student_group = AuthGroup.objects.get_or_create(name='Студенты')[0]
            user.groups.add(student_group)
        
        return student
    
    def _generate_username(self, last_name):
        base = last_name.lower().replace(' ', '_')
        while True:
            suffix = ''.join(random.choices(string.digits, k=4))
            username = f"{base}_{suffix}"
            if not User.objects.filter(username=username).exists():
                return username
    
    def _generate_password(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=12))


class GroupForm(forms.ModelForm):
    """Форма для создания и редактирования групп"""
    class Meta:
        model = EduGroup
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
    """Форма для создания и редактирования расписания"""
    class Meta:
        model = Schedule
        fields = ['group', 'date', 'time', 'classroom', 'topic']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'topic': forms.TextInput(attrs={'placeholder': 'Тема занятия'}),
        }
        labels = {
            'group': 'Группа',
            'date': 'Дата занятия',
            'time': 'Время занятия',
            'classroom': 'Аудитория',
            'topic': 'Тема занятия',
        }
        help_texts = {
            'topic': 'Необязательное поле',
        }
    
    def clean(self):
        """Проверка на конфликты расписания"""
        cleaned_data = super().clean()
        group = cleaned_data.get('group')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        
        if group and date and time:
            # Проверяем, нет ли уже занятия у этой группы в это время
            existing = Schedule.objects.filter(
                group=group,
                date=date,
                time=time
            )
            
            # Если редактируем существующее занятие, исключаем его из проверки
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(
                    f'У группы "{group.name}" уже есть занятие в {date} в {time}'
                )
        
        return cleaned_data


class AttendanceForm(forms.ModelForm):
    """Форма для отметки посещаемости одного студента"""
    class Meta:
        model = Attendance
        fields = ['status', 'note']
        widgets = {
            'note': forms.TextInput(attrs={'placeholder': 'Примечание (необязательно)'}),
        }
        labels = {
            'status': 'Статус',
            'note': 'Примечание',
        }


class AttendanceBulkForm(forms.Form):
    """Форма для массовой отметки посещаемости"""
    pass  # Поля создаются динамически


class PerformanceForm(forms.ModelForm):
    """Форма для выставления оценки"""
    class Meta:
        model = Performance
        fields = ['student', 'grade', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Комментарий (необязательно)'}),
        }
        labels = {
            'student': 'Студент',
            'grade': 'Оценка',
            'comment': 'Комментарий',
        }
    
    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        if group:
            self.fields['student'].queryset = Student.objects.filter(
                enrollments__group=group,
                enrollments__is_active=True
            ).distinct()


class PerformanceBulkForm(forms.Form):
    """Форма для массового выставления оценок группе"""
    date = forms.DateField(
        label='Дата выставления',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )


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
