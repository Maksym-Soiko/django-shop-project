from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	bio = models.TextField(max_length=500, blank=True, verbose_name='Про себе')
	avatar = models.ImageField(upload_to='avatars/%Y/%m/%d/', blank=True, null=True, verbose_name='Аватарка')
	birth_date = models.DateField(null=True, blank=True, verbose_name="Дата народження")
	location = models.CharField(max_length=50, blank=True, verbose_name='Місто')
	website = models.URLField(blank=True, verbose_name='Веб сайт')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'Профіль'
		verbose_name_plural = 'Профілі'

	def __str__(self):
		return f'Профіль користувача {self.user.username}'
	
	@receiver(post_save, sender=User)
	def create_user_profile(sender, instance, created, **kwargs):
		if created:
			Profile.objects.create(user=instance)
 
	@receiver(post_save, sender=User)
	def save_user_profile(sender, instance, **kwargs):
		if hasattr(instance, 'profile'):
			instance.profile.save()