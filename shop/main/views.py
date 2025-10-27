from django.shortcuts import get_object_or_404, render
from .models import Product, Category

def product_list(request, category_slug=None):
	categories = Category.objects.all()
	products = Product.objects.all()

	category = None
	
	if category_slug:
		category = get_object_or_404(Category, slug=category_slug)
		products = products.filter(category=category)

	current_sort = request.GET.get('sort', 'new')

	sort_mapping = {
		'new': '-created_at',
		'old': 'created_at',
		'popular': '-views',
		'price_low': 'price',
		'price_high': '-price',
		'name': 'name',
	}

	order_field = sort_mapping.get(current_sort, sort_mapping['new'])

	try:
		products = products.order_by(order_field)
	except Exception:
		products = products.order_by(sort_mapping['new'])
		current_sort = 'new'

	return render(request, 'main/product_list.html', {
		'products': products,
		'categories': categories,
		'category': category,
		'current_sort': current_sort,
	})


def product_detail(request, id, slug):
	product = get_object_or_404(Product, id=id, slug=slug)
	product.views += 1
	product.save(update_fields=['views'])

	related_products = Product.objects.filter(category=product.category).exclude(id=product.id).order_by('-created_at')[:4]

	return render(request, 'main/product_detail.html', {
		'product': product,
		'related_products': related_products,
	})