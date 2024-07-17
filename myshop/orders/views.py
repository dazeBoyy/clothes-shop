from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from .forms import OrderCreateForm
from .models import OrderItem, Order
from cart.cart import Cart
from .tasks import order_created


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Создаем заказ, но не сохраняем его сразу
            order = form.save(commit=False)

            # Проверяем, есть ли достаточно товара на складе для каждого товара в корзине
            for item in cart:
                product = item['product']
                quantity = item['quantity']
                if product.stock < quantity:
                    return render(request, 'orders/order/create.html', {
                        'cart': cart,
                        'form': form,
                        'error': f'Недостаточно товара {product.name} на складе.'
                    })

            # Если все проверки пройдены, сохраняем заказ и уменьшаем количество товара на складе
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
                del request.session['coupon_id']
            order.save()
            for item in cart:
                product = item['product']
                quantity = item['quantity']
                OrderItem.objects.create(order=order, product=product, price=item['price'], quantity=quantity)
                product.stock -= quantity
                product.save()

            # Очистка корзины
            cart.clear()
            # Отправка уведомления по электронной почте
            order_created.delay(order.id)
            return render(request, 'orders/order/created.html', {'order': order})
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})



@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order/detail.html', {'order': order})