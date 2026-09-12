from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='list'),
    path('favorites/', views.FavoriteListView.as_view(), name='favorite_list'),
    path('<uslug:slug>/', views.ProductDetailView.as_view(), name='detail'),
    path('<uslug:slug>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('<uslug:slug>/review/', views.add_review, name='add_review'),
]
