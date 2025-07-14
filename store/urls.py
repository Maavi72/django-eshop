from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup_view, name='signup_default'),  # now homepage redirects to signup
    path('register/', views.signup_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('home/', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:id>/', views.product_detail, name='product_detail'),
    
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('my-orders/', views.my_orders, name='my_orders'),



    # API Endpoints
    path('api/products/', views.ProductList.as_view(), name='api_product_list'),
    path('api/products/create/', views.ProductListCreateView.as_view(), name='api_product_create'),
    path('api/products/<int:id>/', views.ProductDetailView.as_view(), name='api_product_detail'),

    path('api/orders/', views.OrderListCreateView.as_view(), name='api_order_list_create'),
    path('api/orders/<int:id>/', views.OrderDetailView.as_view(), name='api_order_detail'),

    path('api/register/', views.RegisterUserView.as_view(), name='api_register'),

]
