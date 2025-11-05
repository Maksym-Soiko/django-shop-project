from django import template
from datetime import datetime
from main.models import Product

register = template.Library()

@register.simple_tag
def get_products_count(category=None):
	if category:
		return Product.objects.filter(category=category, is_available=True).count()
	return Product.objects.filter(is_available=True).count()


@register.simple_tag
def user_greeting(user):
    current_hour = datetime.now().hour
    
    if 5 <= current_hour < 12:
        greeting = "Доброго ранку"
    elif 12 <= current_hour < 17:
        greeting = "Добрий день"
    elif 17 <= current_hour < 23:
        greeting = "Добрий вечір"
    else:
        greeting = "Доброї ночі"
    
    if user.is_authenticated:
        name = user.first_name or user.username
        return f"{greeting}, {name}!"
    else:
        return f"{greeting}!"
    

@register.inclusion_tag('main/components/popular_products.html')
def show_popular_products(count=4):
    products = Product.objects.filter(is_available=True).order_by('-views')[:count]
    return {'popular_products': products}