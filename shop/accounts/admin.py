from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

class ProfileInline(admin.StackedInline):
	model = Profile
	can_delete = False
	verbose_name = 'Профіль'

	fields = ('avatar', 'bio', 'birth_date', 'location', 'website', 'created_at', 'updated_at')
	readonly_fields = ('created_at', 'updated_at')

	classes = ('collapse',)


class UserAdmin(BaseUserAdmin):
	inlines = (ProfileInline,)

	list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'get_location')
	list_filter = ('is_staff', 'is_superuser', 'is_active', 'email', 'date_joined')
	search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__location')

	def get_location(self, obj):
		return obj.profile.location if hasattr(obj, 'profile') and obj.profile.location else '-'
	get_location.short_description = 'Місто'


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image_tag', 'location', 'birth_date', 'has_avatar', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'location', 'bio')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Користувач', {
            'fields': ('user',)
        }),
        ('Основна інформація', {
            'fields': ('avatar', 'bio', 'birth_date', 'location', 'website')
        }),
        ('Системна інформація', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_avatar(self, obj):
        return bool(getattr(obj, 'avatar', None))
    has_avatar.boolean = True
    has_avatar.short_description = 'Аватар'
 
    def image_tag(self, odj):
        if not odj:
            return '-'
        avatar = getattr(odj, 'avatar', None)
        if avatar and hasattr(avatar, 'url'):
            return format_html(
                '<img src="{}" style="width:48px; height:48px; object-fit:cover; border-radius:6px;"/>',
                avatar.url
            )
        return format_html('<span style="color:#6b7280;">—</span>')
    image_tag.short_description = "Прев'ю"
 

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)