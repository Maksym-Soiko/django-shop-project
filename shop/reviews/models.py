from django.db import models
from django.contrib.auth.models import User
from main.models import Product

class Review(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')

	RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
	rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='Оцінка')

	title = models.CharField(max_length=100, verbose_name='Заголовок')
	content = models.TextField(max_length=1000, verbose_name='Відгук')
	advantages = models.TextField(blank=True, verbose_name='Переваги')
	disadvantages = models.TextField(blank=True, verbose_name='Недоліки')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	is_active = models.BooleanField(default=True, verbose_name='Активний')
	helpful_count = models.PositiveIntegerField(default=0, verbose_name='Кількість корисних відгуків')

	class Meta:
		verbose_name = 'Відгук'
		verbose_name_plural = 'Відгуки'
		unique_together = ['product', 'author']
		ordering = ['-created_at']

	def __str__(self):
		return f'Відгук від {self.author.username} для {self.product.name} - {self.rating} зірок'
	
	def get_rating_display_stars(self):
		try:
			r = int(self.rating)
		except (TypeError, ValueError):
			r = 0
		if r < 0:
			r = 0
		if r > 5:
			r = 5
		return '★' * r + '☆' * (5 - r)
	get_rating_display_stars.short_description = 'Рейтинг'