from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from decimal import Decimal
from main.models import Category, Product
from .models import Discount, PromoCode, PromoCodeUsage
from .forms import DiscountForm, PromoCodeForm, ApplyPromoCodeForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

def product_discounts(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    qty = request.GET.get('quantity') or request.GET.get('qty') or 1
    try:
        quantity = max(1, int(qty))
    except (ValueError, TypeError):
        quantity = 1

    original_unit_price = getattr(product, 'price', Decimal('0.00'))
    total_original = (original_unit_price or Decimal('0.00')) * quantity

    related = product.discounts.filter(is_active=True)
    valid_discounts = [d for d in related if d.is_valid()]

    best_discount = None
    best_amount = Decimal('0.00')
    for d in valid_discounts:
        try:
            amt = Decimal(d.calculate_discount(original_unit_price, quantity))
        except Exception:
            amt = Decimal('0.00')
        if amt > best_amount:
            best_amount = amt
            best_discount = d

    discounted_total = total_original - best_amount
    if discounted_total < 0:
        discounted_total = Decimal('0.00')

    context = {
        'product': product,
        'quantity': quantity,
        'original_unit_price': original_unit_price,
        'total_original': total_original,
        'discounts': valid_discounts,
        'best_discount': best_discount,
        'best_discount_amount': best_amount,
        'discounted_total': discounted_total,
    }
    return render(request, 'discounts/product_discounts.html', context)


@staff_member_required
def add_discount(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = DiscountForm(request.POST)
        
        if form.is_valid():
            discount = form.save(commit=False)
            discount.product = product
            discount.save()
            
            messages.success(request, f"Знижку для '{product.name}' успішно створено.")
            return redirect(product.get_absolute_url())
        else:
            messages.error(request, "Будь ласка, виправте помилки у формі.")
    else:
        form = DiscountForm()

    return render(request, 'discounts/add_discount.html', {'form': form, 'product': product})


@staff_member_required
def edit_discount(request, discount_id):
	discount = get_object_or_404(Discount, id=discount_id)
	product = getattr(discount, 'product', None)

	if request.method == 'POST':
		form = DiscountForm(request.POST, instance=discount)
		if form.is_valid():
			form.save()
			if product and hasattr(product, 'get_absolute_url'):
				return redirect(product.get_absolute_url())
			try:
				if product:
					return redirect(reverse('product_detail', args=[product.id]))
			except Exception:
				pass
			return redirect('/')
	else:
		form = DiscountForm(instance=discount)

	return render(request, 'discounts/edit_discount.html', {
		'form': form,
		'discount': discount,
		'product': product,
	})


@staff_member_required
@require_POST
def delete_discount(request, discount_id):
	discount = get_object_or_404(Discount, id=discount_id)
	product = getattr(discount, 'product', None)
	discount.delete()
	if product and hasattr(product, 'get_absolute_url'):
		return redirect(product.get_absolute_url())
	try:
		if product:
			return redirect(reverse('product_detail', args=[product.id]))
	except Exception:
		pass
	referer = request.META.get('HTTP_REFERER')
	if referer:
		return redirect(referer)
	return redirect('/')


@staff_member_required
def create_promo_code(request):
	if request.method == 'POST':
		form = PromoCodeForm(request.POST)
		if form.is_valid():
			form.save()
			try:
				return redirect(reverse('discounts:promo_code_list'))
			except Exception:
				return redirect('/promocodes/')
	else:
		form = PromoCodeForm()

	return render(request, 'discounts/promo_code_form.html', {'form': form})


@staff_member_required
def promo_code_list(request):
	categories = Category.objects.all()
	status = request.GET.get('status', 'all')
	q = (request.GET.get('q') or '').strip()

	qs = PromoCode.objects.all()
	if status == 'active':
		qs = qs.filter(is_active=True)
	elif status == 'inactive':
		qs = qs.filter(is_active=False)

	if q:
		qs = qs.filter(Q(code__icontains=q))

	qs = qs.order_by('-id')

	return render(request, 'discounts/promo_code_list.html', {
		'promocodes': qs,
		'status': status,
		'q': q,
        'categories': categories,
	})


@require_POST
@login_required
def apply_promo_code(request):
    form = ApplyPromoCodeForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    code = form.cleaned_data.get('code')
    subtotal = form.cleaned_data.get('subtotal') or Decimal('0.00')

    try:
        promo = PromoCode.objects.get(code__iexact=code)
    except PromoCode.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Промокод не знайдений'}, status=404)

    is_valid = True
    if getattr(promo, 'is_active', None) is False:
        is_valid = False
    if hasattr(promo, 'is_valid') and callable(promo.is_valid):
        try:
            is_valid = promo.is_valid()
        except Exception:
            is_valid = False

    if not is_valid:
        return JsonResponse({'success': False, 'error': 'Промокод недійсний або неактивний'}, status=400)

    discount = Decimal('0.00')
    try:
        if hasattr(promo, 'get_discount_amount') and callable(promo.get_discount_amount):
            discount = Decimal(promo.get_discount_amount(subtotal) or 0)
        elif hasattr(promo, 'amount'):
            discount = Decimal(getattr(promo, 'amount') or 0)
        elif hasattr(promo, 'percent'):
            discount = (subtotal * Decimal(getattr(promo, 'percent') or 0) / Decimal('100')).quantize(Decimal('0.01'))
    except Exception:
        discount = Decimal('0.00')

    if discount < 0:
        discount = Decimal('0.00')
    if discount > subtotal:
        discount = subtotal

    new_total = subtotal - discount

    request.session['applied_promo_code'] = getattr(promo, 'code', str(getattr(promo, 'id', '')))
    request.session['applied_promo_discount'] = str(discount)
    request.session.modified = True

    return JsonResponse({
        'success': True,
        'code': getattr(promo, 'code', ''),
        'discount_amount': str(discount),
        'new_total': str(new_total),
    })


@login_required
def delete_promo_code(request, code_id=None):
    if code_id:
        if not request.user.is_staff:
            messages.error(request, 'У вас немає прав для видалення промокодів.')
            return redirect('discounts:promo_code_list')
        
        promo = get_object_or_404(PromoCode, id=code_id)
        code = promo.code
        promo.delete()
        messages.success(request, f'Промокод "{code}" успішно видалено!')
        return redirect('discounts:promo_code_list')
    else:
        request.session.pop('applied_promo_code', None)
        request.session.pop('applied_promo_id', None)
        request.session.pop('applied_promo_discount', None)
        request.session.modified = True
        
        messages.success(request, 'Промокод видалено з вашого кошика.')
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('main:product_list')


@staff_member_required
def promo_code_stats(request, code_id):
    promo = get_object_or_404(PromoCode, id=code_id)

    usages = PromoCodeUsage.objects.filter(promo_code=promo).select_related('user').order_by('-used_at')

    total_discount = Decimal('0.00')
    usages_count = usages.count()
    
    for usage in usages:
        if usage.discount_amount:
            total_discount += usage.discount_amount

    usages_by_date = {}
    for usage in usages:
        date_key = usage.used_at.strftime('%Y-%m-%d')
        usages_by_date[date_key] = usages_by_date.get(date_key, 0) + 1

    promo.used_count = usages_count
    promo.save(update_fields=['used_count'])

    context = {
        'promo': promo,
        'usages': usages,
        'total_discount': total_discount,
        'total_used_count': usages_count,
        'total_discount_amount': total_discount,
        'usages_count': usages_count,
        'usages_by_date': usages_by_date,
    }
    return render(request, 'discounts/promo_code_stats.html', context)


@login_required
def apply_promo_code_view(request):
    product_id = request.GET.get('product_id')
    product = None
    
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            product = None
    
    if request.method == 'POST':
        form = ApplyPromoCodeForm(request.POST)
        product_id_post = request.POST.get('product_id')
        
        if form.is_valid():
            promo_code = form.cleaned_data['promo_code']
            promo = form.promo
            
            existing_usage = PromoCodeUsage.objects.filter(
                promo_code=promo,
                user=request.user
            ).exists()
            
            if existing_usage:
                messages.warning(
                    request,
                    f'Ви вже використовували промокод "{promo_code}". '
                    f'Кожен промокод можна використати тільки один раз.'
                )
                if product_id_post:
                    return redirect(f"{reverse('discounts:apply_promo_code')}?product_id={product_id_post}")
                return redirect('discounts:apply_promo_code')
            
            if promo.usage_limit:
                current_usage_count = PromoCodeUsage.objects.filter(
                    promo_code=promo
                ).count()
                
                if current_usage_count >= promo.usage_limit:
                    messages.error(
                        request,
                        f'Промокод "{promo_code}" вичерпав ліміт використань.'
                    )
                    if product_id_post:
                        return redirect(f"{reverse('discounts:apply_promo_code')}?product_id={product_id_post}")
                    return redirect('discounts:apply_promo_code')
            
            if 'product_promo_codes' not in request.session:
                request.session['product_promo_codes'] = {}
            
            if product_id_post:
                try:
                    product_obj = Product.objects.get(id=product_id_post)
                    
                    if hasattr(product_obj, 'get_discounted_price'):
                        product_price = product_obj.get_discounted_price()
                    else:
                        product_price = product_obj.price
                    
                    if promo.min_order_amount and product_price < promo.min_order_amount:
                        messages.error(
                            request,
                            f'❌ Промокод "{promo_code}" можна застосувати тільки до товарів вартістю від {promo.min_order_amount:.2f} грн. '
                            f'Ціна цього товару: {product_price:.2f} грн.'
                        )
                        return redirect(f"{reverse('discounts:apply_promo_code')}?product_id={product_id_post}")
                    
                    discount_amount = Decimal('0.00')
                    if promo.discount_type == 'percentage':
                        discount_amount = product_price * (Decimal(str(promo.value)) / Decimal('100'))
                    elif promo.discount_type == 'fixed':
                        discount_amount = min(Decimal(str(promo.value)), product_price)
                    
                    request.session['product_promo_codes'][product_id_post] = {
                        'code': promo_code,
                        'promo_id': promo.id
                    }
                    request.session.modified = True
                    
                    PromoCodeUsage.objects.create(
                        promo_code=promo,
                        user=request.user,
                        order_amount=product_price,
                        discount_amount=discount_amount
                    )
                    
                    messages.success(
                        request,
                        f'🎉 Промокод "{promo_code}" успішно застосовано до товару! '
                        f'Знижка: {discount_amount:.2f} грн. Ціна оновлена з урахуванням знижки.'
                    )
                    
                    return redirect(product_obj.get_absolute_url())
                except Product.DoesNotExist:
                    messages.error(request, 'Товар не знайдено.')
                    return redirect('discounts:apply_promo_code')
            else:
                messages.error(request, 'Оберіть товар для застосування промокоду.')
                return redirect('discounts:apply_promo_code')
        else:
            messages.error(request, 'Помилка при застосуванні промокоду. Перевірте введені дані.')
    else:
        form = ApplyPromoCodeForm()
    
    used_promo_codes = []
    if request.user.is_authenticated:
        used_promo_codes = PromoCodeUsage.objects.filter(
            user=request.user
        ).select_related('promo_code').order_by('-used_at')[:5]
    
    current_promo_code = None
    if product_id:
        product_promo_codes = request.session.get('product_promo_codes', {})
        promo_data = product_promo_codes.get(str(product_id))
        if promo_data:
            current_promo_code = promo_data.get('code')
    
    context = {
        'form': form,
        'title': 'Застосувати промокод',
        'used_promo_codes': used_promo_codes,
        'current_promo_code': current_promo_code,
        'product': product,
    }
    return render(request, 'discounts/apply_promo_code.html', context)


@staff_member_required
def edit_promo_code(request, code_id):
    promo = get_object_or_404(PromoCode, id=code_id)
    
    if request.method == 'POST':
        form = PromoCodeForm(request.POST, instance=promo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Промокод "{promo.code}" успішно оновлено!')
            return redirect('discounts:promo_code_list')
        else:
            messages.error(request, 'Помилка при збереженні. Перевірте введені дані.')
    else:
        form = PromoCodeForm(instance=promo)
    
    context = {
        'form': form,
        'promo': promo,
        'title': f'Редагування промокоду {promo.code}'
    }
    return render(request, 'discounts/edit_promo_code.html', context)