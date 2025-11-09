from django.db import models
from django.urls import reverse
from django.db.models import Avg, Count
from markdownx.models import MarkdownxField

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
	image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
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