from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from education.models import Student, Teacher

class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(max_length=50, required=True, label='Имя')
    last_name = forms.CharField(max_length=50, required=True, label='Фамилия')
    phone = forms.CharField(max_length=20, required=True, label='Телефон')
    birth_date = forms.DateField(
        required=False, 
        label='Дата рождения',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    role = forms.ChoiceField(
        choices=[
            ('student', 'Студент'),
            ('teacher', 'Преподаватель'),
        ],
        label='Роль',
        widget=forms.RadioSelect
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        labels = {
            'username': 'Логин',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            role = self.cleaned_data['role']
            
            if role == 'student':
                Student.objects.create(
                    user=user,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    phone=self.cleaned_data['phone'],
                    birth_date=self.cleaned_data.get('birth_date')
                )
                student_group = Group.objects.get(name='Студенты')
                user.groups.add(student_group)
                
            elif role == 'teacher':
                Teacher.objects.create(
                    user=user,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    phone=self.cleaned_data['phone'],
                    specialization='Не указана'
                )
                teacher_group = Group.objects.get(name='Преподаватели')
                user.groups.add(teacher_group)
        
        return user


class UserLoginForm(AuthenticationForm):
    """Форма входа"""
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'placeholder': 'Введите логин'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'})
    )


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля пользователя"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
        }


class StudentProfileForm(forms.ModelForm):
    """Форма редактирования профиля студента"""
    birth_date = forms.DateField(
        label='Дата рождения',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = Student
        fields = ['middle_name', 'phone', 'birth_date']
        labels = {
            'middle_name': 'Отчество',
            'phone': 'Телефон',
            'birth_date': 'Дата рождения',
        }


class TeacherProfileForm(forms.ModelForm):
    """Форма редактирования профиля преподавателя"""
    class Meta:
        model = Teacher
        fields = ['middle_name', 'specialization', 'phone', 'bio', 'photo']
        labels = {
            'middle_name': 'Отчество',
            'specialization': 'Специализация',
            'phone': 'Телефон',
            'bio': 'Биография',
            'photo': 'Фото',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }