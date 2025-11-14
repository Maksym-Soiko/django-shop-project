from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from main.models import Product
from django.contrib.auth.models import User

class Discount(models.Model):
	DISCOUNT_TYPE_CHOICES = [
		('percentage', 'Відсоток'),
		('fixed', 'Фіксована сума'),
	]

	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='discounts')
	discount_type = models.CharField(choices=DISCOUNT_TYPE_CHOICES)
	value = models.DecimalField(max_digits=10, decimal_places=2)
	start_date = models.DateTimeField()
	end_date = models.DateTimeField()
	is_active = models.BooleanField(default=True)
	min_quantity = models.PositiveIntegerField(default=1)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def is_valid(self):
		if not self.is_active:
			return False
		now = timezone.now()
		return self.start_date <= now <= self.end_date

	def calculate_discount(self, price, quantity):
		if not self.is_valid():
			return 0
		
		if self.min_quantity and quantity < self.min_quantity:
			return 0
		
		if self.discount_type == 'percentage':
			return price * quantity * (self.value / 100)
		elif self.discount_type == 'fixed':
			return self.value * quantity
		
		return 0

	def get_discounted_price(self, price, quantity):
		discount_amount = self.calculate_discount(price, quantity)
		total_price = price * quantity
		discounted_price = total_price - discount_amount
		return max(discounted_price, 0)

	def clean(self):
		super().clean()
		
		if self.discount_type == 'percentage':
			if self.value is not None and (self.value < 0 or self.value > 100):
				raise ValidationError({'value': 'Відсоток знижки повинен бути від 0 до 100'})
		
		elif self.discount_type == 'fixed':
			if self.value <= 0:
				raise ValidationError({'value': 'Фіксована сума знижки повинна бути більше 0'})
		
		if self.start_date and self.end_date and self.start_date >= self.end_date:
			raise ValidationError({'end_date': 'Дата закінчення повинна бути пізніше дати початку'})

	class Meta:
		verbose_name = 'Знижка'
		verbose_name_plural = 'Знижки'
		ordering = ['-created_at']


class PromoCode(models.Model):
	DISCOUNT_TYPE_CHOICES = [
		('percentage', 'Відсоток'),
		('fixed', 'Фіксована сума'),
		('free_shipping', 'Безкоштовна доставка'),
	]

	code = models.CharField(max_length=50, unique=True)
	discount_type = models.CharField(choices=DISCOUNT_TYPE_CHOICES)
	value = models.DecimalField(max_digits=10, decimal_places=2)
	start_date = models.DateTimeField()
	end_date = models.DateTimeField()
	usage_limit = models.PositiveIntegerField(null=True, blank=True)
	used_count = models.PositiveIntegerField(default=0)
	min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	is_active = models.BooleanField(default=True)
	description = models.TextField(blank=True)
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def is_valid(self):
		if not self.is_active:
			return False
		
		now = timezone.now()
		if not (self.start_date <= now <= self.end_date):
			return False
		
		if self.usage_limit is not None and self.used_count >= self.usage_limit:
			return False
		
		return True

	def can_be_used(self):
		if self.usage_limit is None:
			return True
		return self.used_count < self.usage_limit

	def apply_discount(self, order_amount):
		if not self.is_valid():
			return 0
		
		if order_amount < self.min_order_amount:
			return 0
		
		if self.discount_type == 'percentage':
			return order_amount * (self.value / 100)
		elif self.discount_type == 'fixed':
			return min(self.value, order_amount)
		elif self.discount_type == 'free_shipping':
			return 0
		
		return 0

	def increment_usage(self):
		self.used_count += 1
		self.save(update_fields=['used_count'])

	def update_usage_count(self):
		from .models import PromoCodeUsage
		self.used_count = PromoCodeUsage.objects.filter(promo_code=self).count()
		self.save(update_fields=['used_count'])
		return self.used_count

	def get_usage_stats(self):
		from decimal import Decimal
		usages = self.usages.all()
		
		total_discount = sum(usage.discount_amount for usage in usages if usage.discount_amount)
		count = usages.count()
		avg_discount = total_discount / count if count > 0 else Decimal('0.00')
		
		return {
			'total_uses': count,
			'total_discount': total_discount,
			'average_discount': avg_discount,
		}

	def clean(self):
		super().clean()
		
		if self.code:
			self.code = self.code.upper().replace(' ', '')
		
		if self.discount_type in ['percentage', 'fixed']:
			if self.discount_type == 'percentage':
				if self.value < 0 or self.value > 100:
					raise ValidationError({'value': 'Відсоток знижки повинен бути від 0 до 100'})
			elif self.discount_type == 'fixed':
				if self.value <= 0:
					raise ValidationError({'value': 'Фіксована сума знижки повинна бути більше 0'})
		elif self.discount_type == 'free_shipping':
			self.value = 0
		
		if self.start_date and self.end_date and self.start_date >= self.end_date:
			raise ValidationError({'end_date': 'Дата закінчення повинна бути пізніше дати початку'})
		
		if self.min_order_amount is not None and self.min_order_amount < 0:
			raise ValidationError({'min_order_amount': 'Мінімальна сума замовлення не може бути від\'ємною'})

	def get_edit_url(self):
		from django.urls import reverse
		return reverse('discounts:edit_promo_code', kwargs={'code_id': self.pk})
	
	def get_absolute_url(self):
		from django.urls import reverse
		return reverse('discounts:promo_code_stats', kwargs={'code_id': self.pk})

	class Meta:
		verbose_name = 'Промокод'
		verbose_name_plural = 'Промокоди'
		ordering = ['-created_at']


class PromoCodeUsage(models.Model):
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promo_usages')
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='promo_usages', 
        null=True, 
        blank=True
    )
    
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Використання промокоду'
        verbose_name_plural = 'Використання промокодів'
        ordering = ['-used_at']
        unique_together = ('promo_code', 'user', 'product')