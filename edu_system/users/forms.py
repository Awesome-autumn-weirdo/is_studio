from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group  as AuthGroup
from education.models import Student, Teacher
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm


class CustomPasswordChangeForm(PasswordChangeForm):
    """Форма смены пароля (когда пользователь знает старый пароль)"""
    old_password = forms.CharField(
        label='Текущий пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите текущий пароль'})
    )
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите новый пароль'})
    )
    new_password2 = forms.CharField(
        label='Подтверждение нового пароля',
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите новый пароль'})
    )


class ForgotPasswordForm(forms.Form):
    """Форма для восстановления пароля (по email или логину)"""
    email = forms.EmailField(
        label='Email',
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'Введите email, указанный при регистрации'})
    )
    username = forms.CharField(
        label='Логин',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Или введите ваш логин'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')
        
        if not email and not username:
            raise forms.ValidationError('Укажите email или логин для восстановления пароля')
        
        return cleaned_data


class ResetPasswordForm(forms.Form):
    """Форма для установки нового пароля"""
    user_id = forms.IntegerField(widget=forms.HiddenInput())
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите новый пароль'})
    )
    new_password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите новый пароль'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают')
        
        if password1 and len(password1) < 6:
            raise forms.ValidationError('Пароль должен быть не менее 6 символов')
        
        return cleaned_data


class ChangeLoginForm(forms.Form):
    """Форма для смены логина"""
    new_username = forms.CharField(
        label='Новый логин',
        min_length=3,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Введите новый логин'})
    )
    password = forms.CharField(
        label='Подтвердите паролем',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите ваш пароль для подтверждения'})
    )
    
    def clean_new_username(self):
        new_username = self.cleaned_data.get('new_username')
        if User.objects.filter(username=new_username).exists():
            raise forms.ValidationError('Этот логин уже занят. Выберите другой.')
        return new_username


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
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        labels = {
            'username': 'Логин',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
        help_texts = {
            'username': 'Только буквы, цифры и @/./+/-/_',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Создаем профиль студента
            Student.objects.create(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone=self.cleaned_data['phone'],
                birth_date=self.cleaned_data['birth_date']
            )
            
            # Добавляем в группу "Студенты"
            student_group = AuthGroup.objects.get(name='Студенты')
            user.groups.add(student_group)
        
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