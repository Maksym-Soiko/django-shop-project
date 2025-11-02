from django import template
from django.utils import timezone

register = template.Library()

@register.filter(name='currency')
def currency(value, currency='грн'):
	try:
		value = float(value)
		if value.is_integer():
			formatted = f"{int(value):,}".replace(',', ' ')
		else:
			formatted = f"{value:,.2f}".replace(',', ' ').replace('.', ',')
		return f"{formatted} {currency}"
	except (ValueError, TypeError):
		return value

@register.filter
def time_ago(date):
	if not date:
		return ""

	now = timezone.now()
	diff = now - date
	seconds = diff.total_seconds()

	if seconds < 60:
		return "щойно"
	elif seconds < 3600:
		minutes = int(seconds / 60)
		return f"{minutes} хв тому"
	elif seconds < 86400:
		hours = int(seconds / 3600)
		return f"{hours} год тому"
	elif seconds < 604800:
		days = int(seconds / 86400)
		return f"{days} дн тому"
	else:
		return date.strftime("%d.%m.%Y")