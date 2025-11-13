from django import template
from datetime import datetime
from main.models import Product
import json
from django.utils.safestring import mark_safe

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
    

@register.inclusion_tag('main/components/popular_products.html', takes_context=True)
def show_popular_products(context, count=4): 
    products = Product.objects.filter(is_available=True).order_by('-views')[:count]
    
    return {
        'popular_products': products,
        'product_promo_codes': context.get('product_promo_codes'),
        'request': context.get('request'),
    }

class JsonScriptNode(template.Node):
    def __init__(self, value_var, element_id):
        self.value_var = value_var
        self.element_id = element_id

    def render(self, context):
        try:
            value = self.value_var.resolve(context)
        except template.VariableDoesNotExist:
            value = None
        json_text = json.dumps(value, default=str, ensure_ascii=False)
        json_text = json_text.replace('</', '<\\/')
        return mark_safe(f'<script type="application/json" id="{self.element_id}">{json_text}</script>')

@register.tag(name='json_script')
def do_json_script(parser, token):
    bits = token.split_contents()
    if len(bits) != 4 or bits[2] != 'as':
        raise template.TemplateSyntaxError("Usage: {% json_script value as element_id %}")
    value_var = parser.compile_filter(bits[1])
    element_id = bits[3].strip('"\'') 
    return JsonScriptNode(value_var, element_id)