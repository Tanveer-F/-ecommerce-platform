from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from .models import Product, Category, Cart, CartItem, Order
from .forms import CheckoutForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Helper function for retrieving or creating a cart
def get_cart(request):
    cart_id = request.session.get('cart_id')
    if cart_id:
        return get_object_or_404(Cart, id=cart_id)
    cart = Cart.objects.create()
    request.session['cart_id'] = cart.id
    return cart

# Helper function to update cart items quantity
def update_cart(cart, product, quantity=1):
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity = cart_item.quantity + quantity
    cart_item.save()
    return cart_item

# Product listing and details
class ProductListView(ListView):
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        queryset = Product.objects.filter(available=True)
        if category_slug:
            self.category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=self.category)
        else:
            self.category = None
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'product'

    def get_object(self):
        return get_object_or_404(Product, id=self.kwargs.get("id"), slug=self.kwargs.get("slug"), available=True)

# Cart functionality
class CartView(View):
    def get(self, request):
        return render(request, 'store/cart.html', {'cart': get_cart(request)})

class AddToCartView(View):
    def post(self, request, product_id):
        cart = get_cart(request)
        product = get_object_or_404(Product, id=product_id, available=True)
        update_cart(cart, product)
        messages.success(request, f'Added {product.name} to your cart.')
        return redirect('store:cart')

class RemoveFromCartView(View):
    def post(self, request, product_id):
        cart = get_cart(request)
        cart_item = CartItem.objects.filter(cart=cart, product__id=product_id).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, f'Removed {cart_item.product.name} from your cart.')
        return redirect('store:cart')

# Checkout and orders
class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cart = get_cart(request)
        if not cart.items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('store:product_list')
        return render(request, 'store/checkout.html', {'cart': cart, 'form': CheckoutForm()})

    def post(self, request):
        cart = get_cart(request)
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = Order.objects.create(user=request.user, status='paid', total_price=self.calculate_total(cart))
                    cart.items.all().delete()  # Clear cart after placing order
                    messages.success(request, f'Order {order.id} placed successfully!')
                    return redirect('store:order_success', order_id=order.id)
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
        return render(request, 'store/checkout.html', {'cart': cart, 'form': form})

    def calculate_total(self, cart):
        return sum(item.product.price * item.quantity for item in cart.items.all())

class OrderSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'store/order_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = get_object_or_404(Order, id=self.kwargs.get('order_id'), user=self.request.user)
        return context

# User Registration
class RegisterView(View):
    def get(self, request):
        return render(request, 'store/register.html', {'form': UserCreationForm()})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful.')
            next_page = request.GET.get('next', 'store:product_list')  # Redirect to the next page or product list
            return redirect(next_page)
        return render(request, 'store/register.html', {'form': form})
