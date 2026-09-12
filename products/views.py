from django.db.models import Q
from django.views.generic import ListView, DetailView

from .forms import ProductSearchForm
from .models import Product


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
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_active=True)
