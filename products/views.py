from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView, DetailView

from .forms import ProductSearchForm, ReviewForm
from .models import Favorite, Product, Review


def _has_purchased(user, product):
    from orders.models import OrderItem

    return OrderItem.objects.filter(
        order__user=user, order__status='paid', product=product
    ).exists()


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        form = ProductSearchForm(self.request.GET)

        if form.is_valid():
            data = form.cleaned_data
            if data['q']:
                queryset = queryset.filter(
                    Q(name__icontains=data['q']) | Q(description__icontains=data['q'])
                )
            if data['category']:
                queryset = queryset.filter(category=data['category'])
            if data['condition']:
                queryset = queryset.filter(condition=data['condition'])
            if data['min_price'] is not None:
                queryset = queryset.filter(price__gte=data['min_price'])
            if data['max_price'] is not None:
                queryset = queryset.filter(price__lte=data['max_price'])
            queryset = queryset.order_by(data['sort'] or '-created_at')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProductSearchForm(self.request.GET)
        if self.request.user.is_authenticated:
            context['favorite_product_ids'] = set(
                Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True)
            )
        else:
            context['favorite_product_ids'] = set()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_favorited'] = Favorite.objects.filter(
                user=self.request.user, product=self.object
            ).exists()
            context['can_review'] = _has_purchased(self.request.user, self.object)
        else:
            context['is_favorited'] = False
            context['can_review'] = False
        return context


class FavoriteListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'products/favorite_list.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('product', 'product__category')


@login_required
def toggle_favorite(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if not created:
        favorite.delete()
        messages.info(request, f"{product.name}をお気に入りから外しました。")
    else:
        messages.success(request, f"{product.name}をお気に入りに追加しました。")

    next_url = request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('products:detail', slug=slug)


@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    if not _has_purchased(request.user, product):
        messages.error(request, "購入済みの商品のみレビューを投稿できます。")
        return redirect('products:detail', slug=slug)

    existing_review = Review.objects.filter(product=product, user=request.user).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "レビューを投稿しました。")
            return redirect('products:detail', slug=slug)
    else:
        form = ReviewForm(instance=existing_review)

    return render(request, 'products/review_form.html', {'form': form, 'product': product})
