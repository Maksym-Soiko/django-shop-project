from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from main.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        
        self.cart = cart
    
    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)

        price_decimal = Decimal('0')
        try:
            if hasattr(product, 'get_discounted_price'):
                dp = product.get_discounted_price()
                if dp is not None:
                    price_decimal = Decimal(str(dp))
        except Exception:
            price_decimal = Decimal('0')
        if price_decimal == Decimal('0'):
            price_decimal = Decimal(str(getattr(product, 'price', Decimal('0'))))

        product_promo_codes = self.session.get('product_promo_codes', {}) or {}
        promo_identifier = None
        promo_data = product_promo_codes.get(str(product.id)) or product_promo_codes.get(product.id)
        if isinstance(promo_data, dict):
            promo_identifier = promo_data.get('promo_id') or promo_data.get('code') or promo_data.get('id')
        else:
            if promo_data:
                promo_identifier = promo_data
        if not promo_identifier:
            promo_identifier = self.session.get('applied_promo_id') or self.session.get('applied_promo_code')

        if promo_identifier:
            try:
                from discounts.models import PromoCode 
                promo = None
                try:
                    promo = PromoCode.objects.get(id=int(promo_identifier))
                except Exception:
                    try:
                        promo = PromoCode.objects.get(code=str(promo_identifier))
                    except Exception:
                        promo = None

                if promo and getattr(promo, 'is_valid', lambda: True)():
                    min_amount = getattr(promo, 'min_order_amount', Decimal('0'))
                    if price_decimal >= Decimal(str(min_amount)):
                        if hasattr(promo, 'apply_to_price') and callable(promo.apply_to_price):
                            price_decimal = Decimal(str(promo.apply_to_price(price_decimal)))
                        else:
                            if getattr(promo, 'discount_type', None) == 'percentage':
                                price_decimal = price_decimal * (Decimal('1') - Decimal(str(promo.value)) / Decimal('100'))
                            elif getattr(promo, 'discount_type', None) == 'fixed':
                                price_decimal = max(Decimal('0'), price_decimal - Decimal(str(promo.value)))
            except Exception:
                pass

        price_str = str(Decimal(price_decimal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': price_str}

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.cart[product_id]['price'] = price_str
        self.save()
    
    def save(self):
        self.session.modified = True
    
    def remove(self, product):
        product_id = str(product.id)
        
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def __iter__(self):
        product_ids = [int(pid) for pid in self.cart.keys()]
        products = Product.objects.filter(id__in=product_ids).select_related('category')

        cart_copy = self.cart.copy()
        
        for product in products:
            pid = str(product.id)
            if pid in cart_copy:
                cart_copy[pid]['product'] = product
        
        for item in cart_copy.values():
            if 'product' not in item:
                continue
                
            item['quantity'] = int(item.get('quantity', 0))
            
            price_dec = Decimal(str(item.get('price', '0')))
            price_rounded = price_dec.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            item['price_decimal'] = price_rounded
            item['price'] = float(price_rounded)
            
            total_dec = (price_rounded * item['quantity']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            item['total_price_decimal'] = total_dec
            item['total_price'] = float(total_dec)
            
            yield item

    def __len__(self):
        return sum(int(item.get('quantity', 0)) for item in self.cart.values())

    def get_total_price(self):
        total = sum(
            (Decimal(item.get('price', '0')) * int(item.get('quantity', 0)))
            for item in self.cart.values()
        )
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def clear(self):
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()