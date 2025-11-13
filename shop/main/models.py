from django.db import models
from django.urls import reverse
from django.db.models import Avg, Count
from markdownx.models import MarkdownxField
from decimal import Decimal

class Category(models.Model):
	name = models.CharField(max_length=100, db_index=True)
	slug = models.SlugField(max_length=100, unique=True)
	description = models.TextField(blank=True)
	image = models.ImageField(upload_to='categories/', blank=True)
	is_active = models.BooleanField(default=True)

	class Meta:
		verbose_name = "Категорія"
		verbose_name_plural = "Категорії"
		ordering = ['name']

	def __str__(self):
		return self.name
	
	def get_absolute_url(self):
		return reverse('main:product_list_by_category', kwargs={'category_slug': self.slug})

class Product(models.Model):
	category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	slug = models.SlugField(max_length=150, unique=True)
	description = models.TextField()
	detailed_description = MarkdownxField(blank=True, help_text="Детальний опис товару в форматі Markdown")
	image = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	is_available = models.BooleanField(default=True)
	views = models.PositiveIntegerField(default=0)
	featured = models.BooleanField(default=False)

	class Meta:
		verbose_name = "Товар"
		verbose_name_plural = "Товари"

	def __str__(self):
		return self.name
	
	def get_absolute_url(self):
		return reverse('main:product_detail', args=[self.id, self.slug])
	
	def get_average_rating(self):
		avg = self.reviews.filter(is_active=True).aggregate(avg=Avg('rating'))['avg']
		return round(avg, 2) if avg is not None else 0.0
	
	def get_reviews_count(self):
		return self.reviews.filter(is_active=True).count()
	
	def get_rating_distribution(self):
		qs = self.reviews.filter(is_active=True).values('rating').annotate(count=Count('id'))
		dist = {i: 0 for i in range(1, 6)}
		total = 0
		for item in qs:
			r = int(item['rating'])
			c = int(item['count'])
			if 1 <= r <= 5:
				dist[r] = c
				total += c
		
		percent = {i: (round((dist[i] * 100.0 / total), 1) if total else 0.0) for i in dist}
		return {'counts': dist, 'total': total, 'percent': percent}
	
	def get_active_discount(self, quantity=1):
		original_unit_price = getattr(self, 'price', Decimal('0.00')) or Decimal('0.00')
		best = None
		best_amount = Decimal('0.00')
		related = getattr(self, 'discounts', None)
		if related is None:
			return None
		for d in related.filter(is_active=True):
			try:
				if hasattr(d, 'is_valid') and callable(d.is_valid) and not d.is_valid():
					continue
			except Exception:
				continue
			try:
				amt = Decimal(d.calculate_discount(original_unit_price, quantity) or 0)
			except Exception:
				try:
					amt = Decimal(str(d.calculate_discount(original_unit_price, quantity)))
				except Exception:
					amt = Decimal('0.00')
			if amt > best_amount:
				best_amount = amt
				best = d
		return best

	def get_discounted_price(self, quantity=1):
		unit = getattr(self, 'price', Decimal('0.00')) or Decimal('0.00')
		try:
			qty = max(1, int(quantity))
		except Exception:
			qty = 1
		total = (unit * qty).quantize(Decimal('0.01'))
		best = self.get_active_discount(qty)
		if not best:
			return total
		try:
			discount_amount = Decimal(best.calculate_discount(unit, qty) or 0)
		except Exception:
			try:
				discount_amount = Decimal(str(best.calculate_discount(unit, qty)))
			except Exception:
				discount_amount = Decimal('0.00')
		if discount_amount < 0:
			discount_amount = Decimal('0.00')
		if discount_amount > total:
			discount_amount = total
		result = (total - discount_amount).quantize(Decimal('0.01'))
		if result < Decimal('0.00'):
			return Decimal('0.00')
		return result

	def has_active_discount(self):
		return self.get_active_discount() is not None

	def get_discount_percentage(self):
		unit = getattr(self, 'price', Decimal('0.00')) or Decimal('0.00')
		if unit == 0:
			return Decimal('0.00')
		best = self.get_active_discount(1)
		if not best:
			return Decimal('0.00')
		try:
			discount_amount = Decimal(best.calculate_discount(unit, 1) or 0)
		except Exception:
			try:
				discount_amount = Decimal(str(best.calculate_discount(unit, 1)))
			except Exception:
				discount_amount = Decimal('0.00')
		if discount_amount <= 0:
			return Decimal('0.00')
		percent = (discount_amount / unit * Decimal('100')).quantize(Decimal('0.01'))
		return percent