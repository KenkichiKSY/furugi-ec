from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, TemplateView

from products.models import Product

from .models import Cart, Order, OrderItem
from accounts.models import Address

from .shipping import calculate_shipping_fee


def _get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    cart = _get_cart(request.user)
    item, created = cart.items.get_or_create(product=product)
    if not created:
        item.quantity += 1
        item.save()
    messages.success(request, f"{product.name}をカートに追加しました。")
    return redirect('orders:cart_detail')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(Cart, user=request.user).items.filter(id=item_id).first()
    if item:
        item.delete()
    return redirect('orders:cart_detail')


class CartDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/cart_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = _get_cart(self.request.user)
        subtotal = cart.total_price()
        shipping_fee = calculate_shipping_fee(subtotal)
        context['cart'] = cart
        context['subtotal'] = subtotal
        context['shipping_fee'] = shipping_fee
        context['total_with_shipping'] = subtotal + shipping_fee
        context['addresses'] = self.request.user.addresses.all()
        return context


@login_required
def checkout(request):
    cart = _get_cart(request.user)
    items = list(cart.items.select_related('product'))

    if not items:
        messages.error(request, "カートが空です。")
        return redirect('orders:cart_detail')

    address_id = request.POST.get('address_id')
    if not address_id:
        messages.error(request, "配送先を選択してください。")
        return redirect('orders:cart_detail')

    address = get_object_or_404(Address, id=address_id, user=request.user)
    subtotal = cart.total_price()
    shipping_fee = calculate_shipping_fee(subtotal)

    with transaction.atomic():
        for item in items:
            if item.quantity > item.product.stock:
                messages.error(request, f"{item.product.name}の在庫が不足しています。")
                return redirect('orders:cart_detail')

        order = Order.objects.create(
            user=request.user,
            total_price=subtotal + shipping_fee,
            shipping_fee=shipping_fee,
            shipping_recipient_name=address.recipient_name,
            shipping_postal_code=address.postal_code,
            shipping_prefecture=address.prefecture,
            shipping_city=address.city,
            shipping_building=address.building,
            shipping_phone_number=address.phone_number,
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
            )
            item.product.stock -= item.quantity
            item.product.save()
        cart.items.all().delete()

    messages.success(request, "ご注文ありがとうございます。")
    return redirect('orders:order_history')


class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related('items')
            .order_by('-created_at')
        )
