from django.core.management.base import BaseCommand
from discounts.models import PromoCode

class Command(BaseCommand):
    help = 'Оновлює лічильники використання промокодів'

    def handle(self, *args, **options):
        promos = PromoCode.objects.all()
        updated = 0
        
        for promo in promos:
            old_count = promo.used_count
            promo.update_usage_count()
            new_count = promo.used_count
            
            if old_count != new_count:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Промокод {promo.code}: {old_count} -> {new_count}'
                    )
                )
                updated += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Оновлено {updated} промокодів з {promos.count()}'
            )
        )