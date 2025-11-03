from django.db import models
from django.urls import reverse
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