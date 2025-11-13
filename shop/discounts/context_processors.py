from .models import PromoCode

def promo_code_context(request):
    product_promo_codes = request.session.get('product_promo_codes', {})
    
    context = {
        'active_promo_code': None,
        'active_promo': None,
        'product_promo_codes': product_promo_codes,
    }
    
    if request.user.is_authenticated:
        promo_code = request.session.get('applied_promo_code')
        if promo_code:
            try:
                promo = PromoCode.objects.get(code=promo_code)
                if promo.is_valid():
                    context['active_promo_code'] = promo_code
                    context['active_promo'] = promo
                else:
                    request.session.pop('applied_promo_code', None)
                    request.session.pop('applied_promo_id', None)
                    request.session.modified = True
            except PromoCode.DoesNotExist:
                request.session.pop('applied_promo_code', None)
                request.session.pop('applied_promo_id', None)
                request.session.modified = True
    
    return context