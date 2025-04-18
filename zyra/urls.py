from django.urls import path
from zyra import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Sign up and login URLs
    path('', views.user_login, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),  # This matches your signup form action

    # Category and product URLs
    path('category/', views.category_page, name='category_page'),  # Display categories
    path('categories/', views.all_categories, name='all_categories'),  # List all categories
    path('category/<str:category_name>/', views.category_products, name='category_products'),  # Products in a category

    # OTP verification URLs
    path('verify-otp/', views.verify_otp, name='verify_otp'),  # OTP verification page

    # Cart and wishlist URLs
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),  # Add item to cart
    path('cart/', views.view_cart, name='view_cart'),  # View items in cart
    path('wishlist/', views.view_wishlist, name='view_wishlist'),  # View wishlist
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),  # Add product to wishlist
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),  # Remove from wishlist

    # Checkout and order URLs
    path('checkout/', views.checkout_view, name='checkout'),  # Checkout page
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),  # Order success page
    path('order_list/', views.order_list_view, name='order_list'),  # Order list page
    path('order_summary/<int:order_id>/', views.order_summary, name='order_summary'),  # Order summary page

    # Product details
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),  # Product details page

    # Profile and logout URLs
    path('profile/', views.profile, name='profile'),  # User profile page
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  # Logout page

    # OTP sending URL
    path('send-otp/', views.send_otp, name='send_otp'),  # Send OTP to user for verification
    path('add_to_cart/<int:item_id>/', views.add_to_cart_with_id, name='add_to_cart_with_id'),
]