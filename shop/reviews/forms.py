from django import forms
from django.core.exceptions import ValidationError
from .models import Review

_BASE_INPUT_CLASS = (
    "w-full px-4 py-2 border border-gray-200 rounded-lg "
    "focus:outline-none focus:ring-0 focus:border-teal-500 "
    "transition duration-150"
)

class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=Review.RATING_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "peer sr-only"}),
        label="Оцінка",
    )
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": _BASE_INPUT_CLASS,
            "placeholder": "Короткий заголовок (мінімум 5 символів)"
        }),
        label="Заголовок",
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": _BASE_INPUT_CLASS,
            "placeholder": "Розкажіть про свій досвід (мінімум 20 символів)",
            "rows": 6
        }),
        label="Відгук",
    )
    advantages = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": _BASE_INPUT_CLASS,
            "placeholder": "Переваги (необов'язково)",
            "rows": 3
        }),
        label="Переваги",
    )
    disadvantages = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": _BASE_INPUT_CLASS,
            "placeholder": "Недоліки (необов'язково)",
            "rows": 3
        }),
        label="Недоліки",
    )

    class Meta:
        model = Review
        fields = ("rating", "title", "content", "advantages", "disadvantages")

    def clean_title(self):
        title = self.cleaned_data.get("title", "") or ""
        title = title.strip()
        if len(title) < 5:
            raise ValidationError("Заголовок повинен містити щонайменше 5 символів.")
        return title

    def clean_content(self):
        content = self.cleaned_data.get("content", "") or ""
        content = content.strip()
        if len(content) < 20:
            raise ValidationError("Відгук має містити щонайменше 20 символів.")
        return content

    def clean_advantages(self):
        adv = self.cleaned_data.get("advantages", "")
        return adv.strip() if adv else ""

    def clean_disadvantages(self):
        dis = self.cleaned_data.get("disadvantages", "")
        return dis.strip() if dis else ""