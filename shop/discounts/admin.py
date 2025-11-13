from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from django.utils.html import format_html
from .models import Discount, PromoCode, PromoCodeUsage

class DiscountAdmin(admin.ModelAdmin):
    list_display = ('product', 'discount_type', 'value', 'start_date', 'end_date', 'is_active', 'is_valid_now')
    list_filter = ('discount_type', 'is_active', 'start_date')
    search_fields = ('product__name', 'description')
    readonly_fields = ('created_at',)
    list_editable = ('is_active',)
    date_hierarchy = 'start_date'
    actions = ('activate_discounts', 'deactivate_discounts')

    @admin.display(boolean=True, description='Діє зараз')
    def is_valid_now(self, obj):
        try:
            if hasattr(obj, 'is_valid') and callable(obj.is_valid):
                return bool(obj.is_valid())
        except Exception:
            return False

        now = timezone.now()
        if not bool(getattr(obj, 'is_active', False)):
            return False
        start = getattr(obj, 'start_date', None)
        end = getattr(obj, 'end_date', None)
        if start and now < start:
            return False
        if end and now > end:
            return False
        return True


class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'value', 'usage_progress', 'valid_period', 'is_active', 'created_by_display')
    list_filter = ('discount_type', 'is_active', 'created_at')
    search_fields = ('code', 'description')
    readonly_fields = ('used_count', 'created_at')
    fieldsets = (
        ('Основное', {
            'fields': ('code', 'discount_type', 'value', 'description')
        }),
        ('Обмеження', {
            'fields': ('usage_limit', 'min_order_amount', 'start_date', 'end_date')
        }),
        ('Мета', {
            'fields': ('created_by', 'created_at', 'used_count', 'is_active')
        }),
    )
    actions = ('activate_codes', 'deactivate_codes', 'reset_usage')

    @admin.display(description='Прогрес використання')
    def usage_progress(self, obj):
        used = getattr(obj, 'used_count', None)
        limit = getattr(obj, 'usage_limit', None)

        if used is None:
            for rel in ('usages', 'usage_set', 'redemptions', 'redemption_set', 'orders', 'order_set'):
                if hasattr(obj, rel):
                    rel_qs = getattr(obj, rel)
                    try:
                        used = rel_qs.count()
                        break
                    except Exception:
                        try:
                            used = len(list(rel_qs))
                            break
                        except Exception:
                            used = 0
            if used is None:
                used = 0

        if not limit:
            return format_html('<span style="color:#374151;">{} використань</span>', used)

        try:
            percent = int(min(100, max(0, (used * 100) / float(limit))))
        except Exception:
            percent = 0

        bar = format_html(
            '<div style="width:140px;background:#f3f4f6;border-radius:4px;padding:2px;">'
            '<div style="width:{}%;background:#10b981;height:10px;border-radius:3px;"></div></div>'
            '<div style="font-size:11px;color:#374151;">{}/{} ({}%)</div>',
            percent, used, limit, percent
        )
        return bar

    @admin.display(description='Період дії')
    def valid_period(self, obj):
        start = getattr(obj, 'start_date', None)
        end = getattr(obj, 'end_date', None)
        if start and end:
            return "{} — {}".format(
                timezone.localtime(start).strftime('%Y-%m-%d'),
                timezone.localtime(end).strftime('%Y-%m-%d'),
            )
        if start and not end:
            return "з {} ".format(timezone.localtime(start).strftime('%Y-%m-%d'))
        if end and not start:
            return "до {} ".format(timezone.localtime(end).strftime('%Y-%m-%d'))
        return '—'

    @admin.display(description='Створив')
    def created_by_display(self, obj):
        user = getattr(obj, 'created_by', None)
        return str(user) if user else '—'

    def activate_codes(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Активовано {updated} промокодів.", level=messages.SUCCESS)
    activate_codes.short_description = "Активувати вибрані коди"

    def deactivate_codes(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Деактивовано {updated} промокодів.", level=messages.SUCCESS)
    deactivate_codes.short_description = "Деактивувати вибрані коди"

    def reset_usage(self, request, queryset):
        processed = 0
        try:
            updated = queryset.update(used_count=0)
            processed += updated
        except Exception:
            for promo in queryset:
                done = False
                for rel in ('usages', 'usage_set', 'redemptions', 'redemption_set', 'orders', 'order_set'):
                    if hasattr(promo, rel):
                        rel_qs = getattr(promo, rel)
                        try:
                            rel_qs.all().delete()
                            processed += 1
                            done = True
                            break
                        except Exception:
                            continue
                if not done:
                    continue
        self.message_user(request, f"Скинуто використання для {processed} промокодів.", level=messages.SUCCESS)
    reset_usage.short_description = "Скинути лічильник використань"


class PromoCodeUsageAdmin(admin.ModelAdmin):
    list_display = ('promo_code', 'user', 'order_amount', 'discount_amount', 'used_at')
    list_filter = ('used_at', 'promo_code')
    search_fields = ('user__username', 'promo_code__code')
    readonly_fields = [f.name for f in PromoCodeUsage._meta.fields]
    date_hierarchy = 'used_at'
    ordering = ('-used_at',)


admin.site.register(Discount, DiscountAdmin)
admin.site.register(PromoCode, PromoCodeAdmin)
admin.site.register(PromoCodeUsage, PromoCodeUsageAdmin)