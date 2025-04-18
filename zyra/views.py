from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError
from django.utils.crypto import get_random_string
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ImproperlyConfigured
import smtplib

from .forms import CustomUserCreationForm
from .models import Catagory, Product, CartItem, Order, OrderItem

# ------------------------- Home & Authentication -------------------------

def home(request):
    return redirect('signup')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'shopping/signup.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the user and hash the password automatically
            user = form.save()

            # You can add additional fields here if needed
            user.name = form.cleaned_data['name']
            user.phone = form.cleaned_data['phone']
            user.address = form.cleaned_data['address']
            user.gender = form.cleaned_data['gender']
            user.pincode = form.cleaned_data['pincode']
            user.save()  # Save the user with all details
            messages.success(request, 'Your account has been created successfully!')
            return redirect('login')  # Redirect to login page after successful signup
        else :
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'shopping/signup.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        if str(entered_otp) == str(session_otp):
            messages.success(request, "OTP Verified Successfully!")
            request.session['otp_verified'] = True
            return redirect('signup')  # Now allow user to sign up
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'shopping/verify_otp.html')
    return render(request, 'shopping/verify_otp.html')  # Show OTP form
    

from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.http import JsonResponse
import smtplib
from django.core.exceptions import ImproperlyConfigured
def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, "Email is required.")
            return redirect('send_otp')
        
        otp = get_random_string(length=6, allowed_chars='0123456789')
        try:
            send_mail(
                'Your OTP for Signup',
                f'Your OTP is {otp}',
                settings.DEFAULT_FROM_EMAIL,  # Ensure this is set in your settings
                [email],
                fail_silently=False,
            )
            request.session['otp'] = otp
            request.session['email'] = email
            messages.success(request, "OTP sent to your email!")
            return redirect('verify_otp')
        except (smtplib.SMTPException, BadHeaderError, ImproperlyConfigured) as e:
            messages.error(request, f"Email error: {str(e)}")
            return redirect('send_otp')
    # For GET requests, render a template with the email form
    return render(request, 'shopping/send_otp.html')


def user_login(request):
    if request.method == 'POST':
        email = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('category_page')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'shopping/login.html')


# ------------------------- Categories & Products -------------------------

def category_page(request):
    categories = Catagory.objects.filter(status=False)
    cart_item_count = CartItem.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'shopping/category.html', {'categories': categories, 'cart_item_count': cart_item_count})


def all_categories(request):
    categories = Catagory.objects.all()
    return render(request, 'shopping/all_categories.html', {'categories': categories})


def category_products(request, category_name):
    category = get_object_or_404(Catagory, name=category_name)
    products = Product.objects.filter(category=category, status=False)
    return render(request, 'shopping/category_products.html', {
        'category_name': category.name,
        'products': products
    })


# ------------------------- Cart Functionality -------------------------

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
    return redirect('category_page')


@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.selling_price * item.quantity for item in cart_items)
    for item in cart_items:
        item.total_price = item.product.selling_price * item.quantity
    return render(request, 'shopping/cart.html', {'cart_items': cart_items, 'total': total})


def base_view(request):
    cart_item_count = CartItem.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'base.html', {'cart_item_count': cart_item_count})


@login_required
def profile(request):
    return render(request, 'shopping/profile.html', {'user': request.user})


# ------------------------- Checkout & Order -------------------------
@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.selling_price * item.quantity for item in cart_items)

    if request.method == "POST":
        # Create the order
        order = Order.objects.create(user=request.user, total_price=total_price)
        
        # Create order items for each cart item
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.selling_price
            )
        
        # Delete cart items after order creation
        cart_items.delete()

        # Show success message
        messages.success(request, "Payment Successful! Your order has been placed.")
        
        # Redirect to the order summary page
        return redirect('order_summary', order_id=order.id)

    return render(request, "shopping/checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "shopping/order_success.html", {"order": order})


@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'shopping/order_summary.html', {'order': order, 'order_items': order_items})


from django.views.decorators.http import require_POST

@require_POST
@login_required
def update_cart_quantity(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)

    cart_item.quantity = quantity
    cart_item.save()

    return JsonResponse({'success': True, 'new_total': cart_item.product.selling_price * cart_item.quantity})


@login_required
def clear_cart(request):
    CartItem.objects.filter(user=request.user).delete()
    messages.info(request, "Your cart has been cleared.")
    return redirect('view_cart')

@login_required
def order_list_view(request):
    # Get all orders for the logged-in user
    orders = Order.objects.filter(user=request.user)
    return render(request, "shopping/order_list.html", {"orders": orders})

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Wishlist, Product

@login_required
def add_to_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)
    user = request.user

    # Check if the product is already in the wishlist
    wishlist_item = Wishlist.objects.filter(user=user, product=product).first()

    if wishlist_item:
        # If the product is already in the wishlist, remove it
        wishlist_item.delete()
        message = "Removed from wishlist!"
        status = 'removed'
    else:
        # Otherwise, add the product to the wishlist
        Wishlist.objects.create(user=user, product=product)
        message = "Added to wishlist!"
        status = 'added'

    return JsonResponse({
        'message': message,
        'wishlist_status': status,
    })

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    return redirect('view_wishlist')

@login_required
def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'shopping/wishlist.html', {'wishlist_items': wishlist_items})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shopping/product_detail.html', {'product': product})

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect


@login_required
def add_to_cart_with_id(request, item_id):
    # Get the item by its ID
    item = get_object_or_404(Item, id=item_id)

    # Your logic to add the item to the cart
    # Example: adding item to session or cart model
    cart = request.session.get('cart', [])
    cart.append(item.id)  # Assuming you're storing item IDs in the cart
    request.session['cart'] = cart

    return redirect('cart')  # Redirect to the cart or another page

