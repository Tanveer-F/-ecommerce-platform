from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'store'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('category/<slug:category_slug>/', views.ProductListView.as_view(), name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', views.AddToCartView.as_view(), name='cart_add'),
    path('cart/remove/<int:product_id>/', views.RemoveFromCartView.as_view(), name='cart_remove'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order/success/<int:order_id>/', views.OrderSuccessView.as_view(), name='order_success'),

    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),

    # Registration
    path('accounts/register/', views.RegisterView.as_view(), name='register'),

     # Logout
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),


]
