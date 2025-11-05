from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import date
 
class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=100, required=True, label='Ім\'я користувача')
    email = forms.EmailField(required=True, label='Електронна пошта')
    first_name = forms.CharField(max_length=30, required=True, label='Ім\'я')
    last_name = forms.CharField(max_length=30, required=True, label='Прізвище')
    password1 = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Підтвердження пароля')
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4}), label='Про себе')
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='Дата народження')
    location = forms.CharField(max_length=50, required=False, label='Місто')
    website = forms.URLField(required=False, label='Вебсайт')
    avatar = forms.ImageField(required=False, label='Аватарка', help_text='Завантажте фото профілю (JPG, PNG, максимум 5MB)')
 
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
 
        base_input_class = (
            'w-full px-4 py-3 border border-gray-300 rounded-lg '
            'focus:outline-none focus:ring-teal-500 '
            'focus:border-transparent transition duration-150 ease-in-out '
            'bg-white text-gray-900 placeholder:text-gray-400'
        )
 
        placeholders = {
            'email': 'example@email.com',
            'first_name': 'Ваше ім\'я',
            'last_name': 'Ваше прізвище',
            'bio': 'Кілька слів про вас',
            'location': 'Київ, Україна',
            'website': 'https://example.com',
            'username': 'Ім\'я користувача',
            'password1': '******',
            'password2': '******',
        }
       
        help_texts = {
            'password1': "<ul class='list-disc list-inside space-y-1 text-xs text-gray-500'><li>Пароль не повинен бути схожим на ваші особисті дані</li><li>Мінімум 8 символів</li><li>Не може складатися лише з цифр</li></ul>",
            'password2': "Введіть той самий пароль для підтвердження.",
            'username': "Обов'язкове поле. 150 символів або менше. Тільки букви, цифри та символи @/./+/-/_.",
        }
 
        for name, field in self.fields.items():
            field.widget.attrs['class'] = base_input_class
 
            if name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[name]
 
            if name in help_texts:
                field.help_text = help_texts[name]
   
 
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email вже використовується')
        return email
 
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year
            if age < 13:
                raise forms.ValidationError('Мінімальний вік - 13 років')
        return birth_date
   
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
       
        if avatar:
            if avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Розмір файлу не повинен перевищувати 5MB')
           
            if not avatar.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise forms.ValidationError('Дозволені тільки JPG, PNG та GIF файли')
       
        return avatar
 
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
 
        if commit:
            user.save()
            profile = user.profile
            profile.bio = self.cleaned_data.get('bio', '')
            profile.birth_date = self.cleaned_data.get('birth_date')
            profile.location = self.cleaned_data.get('location', '')
            profile.website = self.cleaned_data.get('website', '')
           
            avatar = self.cleaned_data.get('avatar')
            if avatar:
                profile.avatar = avatar
           
            profile.save()
            
        return user