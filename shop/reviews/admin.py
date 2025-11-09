from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'product', 'rating', 'title_preview', 'created_at', 'is_active', 'helpful_count')
    list_filter = ('rating', 'is_active', 'created_at')
    search_fields = ('author__username', 'product__name', 'title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)
    ordering = ('-created_at',)

    fieldsets = (
        ('Основне', {
            'fields': ('product', 'author', 'rating', 'title', 'content')
        }),
        ('Додаткове', {
            'fields': ('advantages', 'disadvantages', 'is_active', 'helpful_count')
        }),
        ('Системна інформація', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    actions = ('activate_reviews', 'deactivate_reviews')

    def title_preview(self, obj):
        if not obj.title:
            return '-'
        text = obj.title
        return text if len(text) <= 50 else f"{text[:47]}..."
    title_preview.short_description = 'Заголовок'

    def activate_reviews(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _("%d відгуків активовано.") % updated)
    activate_reviews.short_description = _("Активувати відгуки")

    def deactivate_reviews(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _("%d відгуків деактивовано.") % updated)
    deactivate_reviews.short_description = _("Деактивувати відгуви")

admin.site.register(Review, ReviewAdmin)