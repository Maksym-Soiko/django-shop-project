from django.shortcuts import get_object_or_404, render
from .models import Product, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import re

def product_list(request, category_slug=None):
	categories = Category.objects.all()
	products = Product.objects.all()

	category = None
	search_query = request.GET.get('q')
	
	if category_slug:
		category = get_object_or_404(Category, slug=category_slug)
		products = products.filter(category=category)

	if search_query:
		search_query = search_query.strip()
		escaped_query = re.escape(search_query)
		products = products.filter(
			Q(name__iregex=escaped_query) |
			Q(description__iregex=escaped_query) |
			Q(category__name__iregex=escaped_query)
		)

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

	paginator = Paginator(products, 8)
	page = request.GET.get('page')
	try:
		products = paginator.page(page)
	except PageNotAnInteger:
		products = paginator.page(1)
	except EmptyPage:
		products = paginator.page(paginator.num_pages)

	return render(request, 'main/product_list.html', {
		'products': products,
		'categories': categories,
		'category': category,
		'current_sort': current_sort,
		'search_query': search_query,
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