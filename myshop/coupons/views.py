from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Coupon
from .forms import CouponApplyForm

@require_POST
def coupon_apply(request):
    now = timezone.now()
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code,
                                        valid_from__lte=now,
                                        valid_to__gte=now,
                                        active=True)
            request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None  # Clear the coupon ID from session
            form.add_error('code', 'This coupon does not exist or is not valid.')
    # Always redirect back to the cart or checkout page, regardless of coupon existence
    return redirect('cart:cart_detail')


def coupon_remove(request):
    if request.method == 'POST':
        del request.session['coupon_id']

    return redirect('cart:cart_detail')