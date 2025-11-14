from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.conf import settings
import logging
from main.models import Product, Category
from .cart import Cart
from .forms import CartAddProductForm
from django.contrib import messages

logger = logging.getLogger(__name__)

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        product_promo_codes = request.session.get('product_promo_codes', {})
        logger.debug("cart_add: product_id=%s, session.product_promo_codes=%s", product_id, product_promo_codes)
        try:
            cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'])
            messages.success(request, "Товар додано до кошика.")
        except Exception as e:
            logger.exception("cart_add: error while adding product %s: %s", product_id, e)
            messages.error(request, "Сталася помилка при додаванні товару. Спробуйте пізніше.")
        try:
            logger.debug("cart_add: cart after add = %s", request.session.get(settings.CART_SESSION_ID))
        except Exception:
            logger.debug("cart_add: unable to read cart from session")
    else:
        logger.error("cart_add: Форма невалідна: %s", form.errors)
        messages.error(request, "Некоректні дані форми. Перевірте кількість.")

    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')

@require_POST
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    categories = Category.objects.all()
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item.get('quantity', 0), 'override': True}
        )
    return render(request, 'cart/cart_detail.html', {'cart': cart, 'categories': categories})