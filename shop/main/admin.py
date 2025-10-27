from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'slug', 'is_active', 'image_tag')
	list_filter = ('is_active',)
	search_fields = ('name',)
	prepopulated_fields = {'slug': ('name',)}
	list_editable = ('is_active',)

	def image_tag(self, obj):
		if obj.image:
			return format_html('<a href="{}"><img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px" /></a>', obj.image.url, obj.image.url)
		return format_html('<span style="color: gray; width: 50px; height: 50px; border-radius: 4px"></span>')
	image_tag.short_description = 'Image'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'category', 'price', 'is_available', 'featured', 'views', 'image_tag')
	list_filter = ('category', 'is_available', 'featured', 'created_at')
	search_fields = ('name', 'description')
	prepopulated_fields = {'slug': ('name',)}
	list_editable = ('price', 'is_available', 'featured')
	ordering = ('-created_at',)

	def image_tag(self, obj):
		if obj.image:
			return format_html('<a href="{}"><img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px" /></a>', obj.image.url, obj.image.url)
		return format_html('<span style="color: gray; width: 50px; height: 50px; border-radius: 4px"></span>')
	image_tag.short_description = 'Image'