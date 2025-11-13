from django import forms
from django.core.exceptions import ValidationError
from .models import Discount, PromoCode

_BASE_INPUT_CLASS = (
    "w-full px-4 py-2 border border-gray-200 rounded-lg "
    "focus:outline-none focus:ring-0 focus:border-teal-500 "
    "transition duration-150"
)

class DiscountForm(forms.ModelForm):
    discount_type = forms.ChoiceField(
        choices=Discount.DISCOUNT_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "space-x-4"}),
        label='Тип знижки'
    )
    
    value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": _BASE_INPUT_CLASS, "placeholder": "0.00"}),
        label='Значення'
    )
    
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            "type": "datetime-local",
            "class": _BASE_INPUT_CLASS,
            "placeholder": "YYYY-MM-DDTHH:MM"
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
        label='Дата початку'
    )
    
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            "type": "datetime-local",
            "class": _BASE_INPUT_CLASS,
            "placeholder": "YYYY-MM-DDTHH:MM"
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
        label='Дата закінчення'
    )
    
    min_quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": _BASE_INPUT_CLASS, "placeholder": "1"}),
        initial=1,
        label='Мінімальна кількість'
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": _BASE_INPUT_CLASS, "rows": 4, "placeholder": "Опис (необов'язково)"}),
        label='Опис'
    )

    class Meta:
        model = Discount
        fields = ['discount_type', 'value', 'start_date', 'end_date', 'min_quantity', 'description']

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

    def clean_value(self):
        value = self.cleaned_data.get('value')
        discount_type = self.cleaned_data.get('discount_type')
        
        if value is None:
            raise ValidationError('Введіть значення знижки')
            
        if discount_type == 'percentage':
            if value < 0 or value > 100:
                raise ValidationError('Відсоток знижки повинен бути від 0 до 100')
        elif discount_type == 'fixed':
            if value <= 0:
                raise ValidationError('Фіксована сума знижки повинна бути більше 0')
            
            if self.product and value > self.product.price:
                raise ValidationError(
                    f'Фіксована знижка ({value} грн) не може бути більшою за ціну товару ({self.product.price} грн)'
                )
        
        return value

    def clean_min_quantity(self):
        min_q = self.cleaned_data.get('min_quantity')
        if min_q is None:
            return 1
        if min_q < 1:
            raise ValidationError('Мінімальна кількість повинна бути не менше 1')
        return min_q

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and start >= end:
            raise ValidationError({'end_date': 'Дата закінчення повинна бути пізніше дати початку'})
        return cleaned


class PromoCodeForm(forms.ModelForm):
    code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={"class": _BASE_INPUT_CLASS, "placeholder": "Наприклад: PROMO2025"}),
        label='Код'
    )
    
    discount_type = forms.ChoiceField(
        choices=PromoCode.DISCOUNT_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": _BASE_INPUT_CLASS}),
        label='Тип знижки'
    )
    
    value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": _BASE_INPUT_CLASS, "placeholder": "0.00"}),
        label='Значення'
    )
    
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            "type": "datetime-local",
            "class": _BASE_INPUT_CLASS,
            "placeholder": "YYYY-MM-DDTHH:MM"
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
        label='Дата початку'
    )
    
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            "type": "datetime-local",
            "class": _BASE_INPUT_CLASS,
            "placeholder": "YYYY-MM-DDTHH:MM"
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
        label='Дата закінчення'
    )
    
    usage_limit = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"class": _BASE_INPUT_CLASS, "placeholder": "Ліміт використань"}),
        label='Ліміт використань'
    )
    
    min_order_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=0,
        widget=forms.NumberInput(attrs={"class": _BASE_INPUT_CLASS, "placeholder": "0.00"}),
        label='Мін. сума замовлення'
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": _BASE_INPUT_CLASS, "rows": 4, "placeholder": "Опис (необов'язково)"}),
        label='Опис'
    )

    class Meta:
        model = PromoCode
        fields = [
            'code', 'discount_type', 'value', 'start_date', 'end_date',
            'usage_limit', 'min_order_amount', 'description'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['code'].disabled = True
            self.fields['code'].widget.attrs['readonly'] = True
            self.fields['code'].help_text = 'Код промокоду не можна змінити після створення'

    def clean_code(self):
        code = self.cleaned_data.get('code', '') or ''
        cleaned = code.upper().replace(' ', '')
        if len(cleaned) < 4:
            raise ValidationError('Код повинен містити щонайменше 4 символи')
        return cleaned

    def clean_value(self):
        value = self.cleaned_data.get('value')
        discount_type = self.cleaned_data.get('discount_type')
        
        if discount_type == 'free_shipping':
            return 0
            
        if value is None:
            raise ValidationError('Введіть значення знижки')
            
        if discount_type == 'percentage':
            if value < 0 or value > 100:
                raise ValidationError('Відсоток знижки повинен бути від 0 до 100')
        elif discount_type == 'fixed':
            if value <= 0:
                raise ValidationError('Фіксована сума знижки повинна бути більше 0')
        return value

    def clean_usage_limit(self):
        usage = self.cleaned_data.get('usage_limit')
        if usage is None:
            return None
        if usage <= 0:
            raise ValidationError('Ліміт використань повинен бути більше 0 або порожнім')
        return usage

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        
        if start and end and start >= end:
            raise ValidationError({'end_date': 'Дата закінчення повинна бути пізніше дати початку'})

        min_amount = cleaned.get('min_order_amount')
        if min_amount is not None and min_amount < 0:
            raise ValidationError({'min_order_amount': "Мінімальна сума замовлення не може бути від'ємною"})

        # Нормалізація коду
        if 'code' in cleaned and cleaned['code']:
            cleaned['code'] = cleaned['code'].upper().replace(' ', '')
            
        return cleaned


class ApplyPromoCodeForm(forms.Form):
	promo_code = forms.CharField(
		max_length=50,
		widget=forms.TextInput(attrs={"class": _BASE_INPUT_CLASS, "placeholder": "Введіть код промокоду"}),
		label='Промокод'
	)

	def clean_promo_code(self):
		code = self.cleaned_data.get('promo_code', '') or ''
		cleaned = code.upper().replace(' ', '')
		if not cleaned:
			raise ValidationError('Введіть код промокоду')

		try:
			promo = PromoCode.objects.get(code=cleaned)
		except PromoCode.DoesNotExist:
			raise ValidationError('Промокод не знайдено')

		if not promo.is_valid():
			raise ValidationError('Промокод недійсний або не може бути використаний')

		self.cleaned_data['promo_code'] = cleaned
		self.promo = promo
		return cleaned