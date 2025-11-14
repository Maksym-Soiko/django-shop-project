from django import forms

class CartAddProductForm(forms.Form):
	quantity = forms.IntegerField(
		min_value=1,
		max_value=99,
		initial=1,
		widget=forms.NumberInput(attrs={
			'class': 'p-2 border-2 border-gray-400 rounded-lg w-12 max-w-full text-center text-sm font-bold small-number-input',
			'placeholder': '1',
			'inputmode': 'numeric',
		})
	)
	override = forms.BooleanField(
		required=False,
		initial=False,
		widget=forms.HiddenInput()
	)