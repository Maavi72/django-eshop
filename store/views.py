from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

from django.views.decorators.csrf import csrf_protect, csrf_exempt
import json



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer, RegisterSerializer

# -----------------------------
# HTML TEMPLATE VIEWS
# -----------------------------

@login_required
def home(request):
    featured_products = Product.objects.filter(is_active=True)[:3]
    return render(request, 'store/home.html', {'featured_products': featured_products})


@login_required
def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'store/product_list.html', {'products': products})


@login_required
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'store/product_detail.html', {'product': product})


@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = product.price * quantity
        total += item_total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': item_total,
        })

    return render(request, 'store/cart.html', {'cart_items': cart_items, 'cart_total': total})


@login_required
@csrf_protect
@login_required
@csrf_protect
def checkout(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        payment = request.POST.get('payment')
        cart = request.session.get('cart', {})

        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            total_price = product.price * quantity

            Order.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,
                total_price=total_price,  # ✅ Add this line
                status='Pending'
            )

        request.session['cart'] = {}  # Clear cart after order
        return redirect('home')

    return render(request, 'store/checkout.html')



def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:
            User.objects.create_user(username=username, email=email, password=password1)
            return redirect('login')  # 🔄 Go to login after signup
        else:
            return render(request, 'store/signup.html', {'error': 'Passwords do not match'})

    return render(request, 'store/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('product_list')  # 🔄 Go to product list after login
        else:
            return render(request, 'store/login.html', {'error': 'Invalid credentials'})
    return render(request, 'store/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@csrf_exempt
@login_required
def add_to_cart(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
            cart = request.session.get('cart', {})
            cart[str(id)] = cart.get(str(id), 0) + quantity
            request.session['cart'] = cart
            return JsonResponse({'success': True, 'message': 'Product added to cart.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


# -----------------------------
# API VIEWS (DRF)
# -----------------------------

class ProductList(APIView):
    def get(self, request):
        products = Product.objects.filter(is_active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'price']


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'product']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


@require_POST
@login_required
@csrf_protect
def remove_from_cart(request, id):
    cart = request.session.get('cart', {})
    product_id = str(id)

    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart

    return redirect('cart')

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')  # ✅ FIXED
    return render(request, 'store/my_orders.html', {'orders': orders})





