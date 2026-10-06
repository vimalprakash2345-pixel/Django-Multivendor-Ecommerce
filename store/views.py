from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Avg

from .models import (
    Product,
    Cart,
    Order,
    OrderItem,
    Wishlist,
    Review,
    BuyerAccount,
    SellerAccount
)


# =========================
# BUYER HOME
# =========================

def home(request):

    # Buyer can see ALL sellers' products
    products = Product.objects.all()

    search = request.GET.get('search')
    category = request.GET.get('category')

    if search:
        products = products.filter(
            name__icontains=search
        )

    if category:
        products = products.filter(
            category=category
        )

    categories = Product.objects.values_list(
        'category',
        flat=True
    ).distinct()

    return render(
        request,
        'store/home.html',
        {
            'products': products,
            'categories': categories
        }
    )


# =========================
# WISHLIST
# =========================

@login_required
def add_to_wishlist(request, product_id):

    product = Product.objects.get(id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect(
        'product_detail',
        product_id=product.id
    )


@login_required
def wishlist(request):

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('product')

    return render(
        request,
        'store/wishlist.html',
        {
            'wishlist_items': wishlist_items
        }
    )


@login_required
def remove_from_wishlist(request, product_id):

    Wishlist.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()

    return redirect('wishlist')


# =========================
# SELLER HOME
# =========================

@login_required
def seller_home(request):

    if not SellerAccount.objects.filter(
        user=request.user
    ).exists():

        return redirect('seller_login')

    return render(
        request,
        'store/seller_home.html'
    )


# =========================
# SELLER DASHBOARD
# =========================

@login_required
def seller_dashboard(request):

    if not SellerAccount.objects.filter(user=request.user).exists():
        return redirect('seller_login')

    products = Product.objects.filter(
        seller=request.user
    ).order_by('-created_at')

    return render(
        request,
        'store/seller_dashboard.html',
        {
            'products': products,
            'seller': request.user
        }
    )


# =========================
# ADD PRODUCT
# =========================

@login_required
def add_product(request):

    if not SellerAccount.objects.filter(user=request.user).exists():
        return redirect('seller_login')

    if request.method == 'POST':

        name = request.POST.get('name')
        category = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')

        Product.objects.create(
            seller=request.user,
            name=name,
            category=category,
            description=description,
            price=price,
            stock=stock,
            image=image
        )

        return redirect('seller_dashboard')

    return render(request, 'store/add_product.html')
# =========================
# EDIT PRODUCT
# =========================

@login_required
def edit_product(request, product_id):

    # Check seller account
    if not SellerAccount.objects.filter(
        user=request.user
    ).exists():

        return redirect('seller_login')

    # IMPORTANT:
    # Seller can edit ONLY their own product
    product = Product.objects.filter(
        id=product_id,
        seller=request.user
    ).first()

    if product is None:
        return redirect('seller_dashboard')

    if request.method == 'POST':

        product.name = request.POST.get('name')
        product.category = request.POST.get('category')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()

        return redirect('seller_dashboard')

    return render(
        request,
        'store/edit_product.html',
        {
            'product': product
        }
    )


# =========================
# DELETE PRODUCT
# =========================

@login_required
def delete_product(request, product_id):

    # Check seller account
    if not SellerAccount.objects.filter(
        user=request.user
    ).exists():

        return redirect('seller_login')

    # IMPORTANT:
    # Seller can delete ONLY their own product
    product = Product.objects.filter(
        id=product_id,
        seller=request.user
    ).first()

    if product is None:
        return redirect('seller_dashboard')

    product.delete()

    return redirect('seller_dashboard')


# =========================
# SELLER ORDERS
# =========================

@login_required
def seller_orders(request):

    if not SellerAccount.objects.filter(
        user=request.user
    ).exists():

        return redirect('seller_login')

    orders = Order.objects.filter(
        items__seller=request.user
    ).distinct().order_by(
        '-created_at'
    )

    return render(
        request,
        'store/seller_orders.html',
        {
            'orders': orders
        }
    )


# =========================
# UPDATE ORDER STATUS
# =========================

@login_required
def update_order_status(request, order_id):

    if not SellerAccount.objects.filter(
        user=request.user
    ).exists():

        return redirect('seller_login')

    order = Order.objects.get(
        id=order_id
    )

    if request.method == 'POST':

        status = request.POST.get('status')

        order.status = status
        order.save()

    return redirect('seller_orders')


# =========================
# CART
# =========================

@login_required
def add_to_cart(request, product_id):

    product = Product.objects.get(
        id=product_id
    )

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:

        cart_item.quantity += 1
        cart_item.save()

    return redirect('home')


@login_required
def cart(request):

    cart_items = Cart.objects.filter(
        user=request.user
    ).select_related('product')

    total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    return render(
        request,
        'store/cart.html',
        {
            'cart_items': cart_items,
            'total': total
        }
    )


@login_required
def increase_quantity(request, cart_id):

    cart_item = Cart.objects.get(
        id=cart_id,
        user=request.user
    )

    if cart_item.quantity < cart_item.product.stock:

        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')


@login_required
def decrease_quantity(request, cart_id):

    cart_item = Cart.objects.get(
        id=cart_id,
        user=request.user
    )

    if cart_item.quantity > 1:

        cart_item.quantity -= 1
        cart_item.save()

    else:

        cart_item.delete()

    return redirect('cart')


@login_required
def remove_from_cart(request, cart_id):

    cart_item = Cart.objects.get(
        id=cart_id,
        user=request.user
    )

    cart_item.delete()

    return redirect('cart')


# =========================
# CHECKOUT
# =========================

@login_required
def checkout(request):

    cart_items = Cart.objects.filter(
        user=request.user
    ).select_related('product')

    total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    if request.method == 'POST':

        customer_name = request.POST.get('customer_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        order = Order.objects.create(
            user=request.user,
            customer_name=customer_name,
            email=email,
            phone=phone,
            address=address,
            total_amount=total
        )

        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                seller=item.product.seller,
                quantity=item.quantity,
                price=item.product.price
            )

        Cart.objects.filter(
            user=request.user
        ).delete()

        return render(
            request,
            'store/order_success.html',
            {
                'order': order
            }
        )

    return render(
        request,
        'store/checkout.html',
        {
            'cart_items': cart_items,
            'total': total
        }
    )


# =========================
# MY ORDERS
# =========================

@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'store/my_orders.html',
        {
            'orders': orders
        }
    )


# =========================
# CANCEL ORDER
# =========================

@login_required
def cancel_order(request, order_id):

    order = Order.objects.get(
        id=order_id,
        user=request.user
    )

    if order.status == 'Pending':

        order.status = 'Cancelled'
        order.save()

    return redirect('my_orders')


# =========================
# PRODUCT DETAILS
# =========================

def product_detail(request, product_id):

    product = Product.objects.get(
        id=product_id
    )

    reviews = Review.objects.filter(
        product=product
    ).order_by('-created_at')

    average_rating = reviews.aggregate(
        average=Avg('rating')
    )['average']

    review_count = reviews.count()

    return render(
        request,
        'store/product_detail.html',
        {
            'product': product,
            'reviews': reviews,
            'average_rating': average_rating,
            'review_count': review_count
        }
    )


# =========================
# ADD REVIEW
# =========================

@login_required
def add_review(request, product_id):

    product = Product.objects.get(
        id=product_id
    )

    if request.method == 'POST':

        rating = int(
            request.POST.get('rating')
        )

        comment = request.POST.get(
            'comment'
        )

        if rating < 1 or rating > 5:

            return redirect(
                'product_detail',
                product_id=product.id
            )

        existing_review = Review.objects.filter(
            user=request.user,
            product=product
        ).first()

        if existing_review:

            return redirect(
                'product_detail',
                product_id=product.id
            )

        Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            comment=comment
        )

        return redirect(
            'product_detail',
            product_id=product.id
        )

    return redirect(
        'product_detail',
        product_id=product.id
    )


# =========================
# BUYER LOGIN
# =========================

def buyer_login(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if BuyerAccount.objects.filter(
                user=user
            ).exists():

                login(request, user)

                return redirect('home')

        return render(
            request,
            'store/buyer_login.html',
            {
                'error': 'Invalid Buyer account'
            }
        )

    return render(
        request,
        'store/buyer_login.html'
    )


# =========================
# SELLER LOGIN
# =========================

def seller_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        print("LOGIN USERNAME:", username)
        print("AUTHENTICATED USER:", user)

        if user is not None:

            seller_exists = SellerAccount.objects.filter(
                user=user
            ).exists()

            print("SELLER ACCOUNT:", seller_exists)

            if seller_exists:

                login(request, user)

                print("SESSION USER AFTER LOGIN:", request.user.username)

                return redirect('seller_home')

            return render(
                request,
                'store/seller_login.html',
                {
                    'error': 'This is not a Seller account'
                }
            )

        return render(
            request,
            'store/seller_login.html',
            {
                'error': 'Invalid username or password'
            }
        )

    return render(
        request,
        'store/seller_login.html'
    )

# =========================
# BUYER REGISTER
# =========================

def buyer_register(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        email = request.POST.get(
            'email'
        )

        password = request.POST.get(
            'password'
        )

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                'store/buyer_register.html',
                {
                    'error': 'Username already exists'
                }
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        BuyerAccount.objects.create(
            user=user
        )

        return redirect('buyer_login')

    return render(
        request,
        'store/buyer_register.html'
    )


# =========================
# SELLER REGISTER
# =========================

def seller_register(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        email = request.POST.get(
            'email'
        )

        password = request.POST.get(
            'password'
        )

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                'store/seller_register.html',
                {
                    'error': 'Username already exists'
                }
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        SellerAccount.objects.create(
            user=user
        )

        return redirect('seller_login')

    return render(
        request,
        'store/seller_register.html'
    )


# =========================
# OLD LOGIN
# =========================

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('home')

        return render(
            request,
            'store/login.html',
            {
                'error': 'Invalid username or password'
            }
        )

    return render(
        request,
        'store/login.html'
    )


# =========================
# LOGOUT
# =========================

def logout_view(request):

    is_seller = SellerAccount.objects.filter(
        user=request.user
    ).exists()

    logout(request)

    if is_seller:
        return redirect('seller_login')

    return redirect('home')

# =========================
# OLD REGISTER
# =========================

def register(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        email = request.POST.get(
            'email'
        )

        password = request.POST.get(
            'password'
        )

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                'store/register.html',
                {
                    'error': 'Username already exists'
                }
            )

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('login')

    return render(
        request,
        'store/register.html'
    )