from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from .forms import CheckoutForm
from .models import Product, Order, OrderItem
from django.views.decorators.http import require_POST
import hmac
import os

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


def index(request):
    products = Product.objects.all()
    return render(request, 'products/index.html', {'products':
                                              products})


def new(request):
    return HttpResponse('New Products')



@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})
    product_id = str(product.id)

    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart

    messages.success(request, f"{product.name} added to cart!")

    return redirect('index')



def cart(request):
    cart_items = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart_items.keys())

    items = []
    total = 0

    for product in products:
        quantity = cart_items.get(str(product.id), 0)
        subtotal = product.price * quantity
        total += subtotal

        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    return render(request, 'products/cart.html', {
        'items': items,
        'total': total,
    })


@require_POST
def update_cart(request, product_id):
    cart_items = request.session.get('cart', {})
    product_key = str(product_id)

    if product_key not in cart_items:
        messages.error(request, 'That product is not in your cart.')
        return redirect('cart')

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        messages.error(request, 'Please enter a valid quantity.')
        return redirect('cart')

    if quantity < 1:
        messages.error(request, 'Quantity must be at least 1.')
        return redirect('cart')

    if not Product.objects.filter(id=product_id).exists():
        cart_items.pop(product_key, None)
        request.session['cart'] = cart_items
        messages.error(request, 'That product no longer exists.')
        return redirect('cart')

    cart_items[product_key] = quantity
    request.session['cart'] = cart_items
    messages.success(request, 'Cart quantity updated.')

    return redirect('cart')


@require_POST
def remove_from_cart(request, product_id):
    cart_items = request.session.get('cart', {})
    cart_items.pop(str(product_id), None)
    request.session['cart'] = cart_items

    messages.success(request, 'Product removed from cart.')
    return redirect('cart')



from decimal import Decimal


def build_order_items(cart, lock=False):
    product_ids = list(cart.keys())
    products = Product.objects.filter(id__in=product_ids)

    if lock:
        products = products.select_for_update()

    items = []
    total = Decimal('0.00')

    for product in products:
        try:
            quantity = int(cart[str(product.id)])
        except (KeyError, TypeError, ValueError):
            raise ValueError("Your cart contains an invalid quantity.")

        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        if product.stock < quantity:
            raise ValueError(
                f"Only {product.stock} unit(s) of {product.name} "
                "are available."
            )

        price = Decimal(str(product.price))
        subtotal = price * quantity
        total += subtotal

        items.append({
            'product': product,
            'quantity': quantity,
            'price': price,
            'subtotal': subtotal,
        })

    if len(items) != len(product_ids):
        raise ValueError("A product in your cart no longer exists.")

    if not items:
        raise ValueError("Your cart is empty.")

    return items, total


def checkout(request):
    cart_items = request.session.get('cart', {})

    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    try:
        items, total = build_order_items(cart_items)
    except ValueError as e:
        messages.warning(request, str(e))
        return redirect('cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                # Recheck stock and prices inside the transaction
                items, total = build_order_items(cart_items, lock=True)

                order = Order.objects.create(
                    customer_name=form.cleaned_data['customer_name'],
                    phone=form.cleaned_data['phone'],
                    address=form.cleaned_data['address'],
                    total=total,
                )

                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        product_name=item['product'].name,
                        quantity=item['quantity'],
                        price=item['price'],
                    )

                    item['product'].stock -= item['quantity']
                    item['product'].save(update_fields=['stock'])

            request.session['cart'] = {}
            request.session.modified = True

            return render(
                request,
                'products/order_success.html',
                {'order': order}
            )
    else:
        form = CheckoutForm()

    return render(request, 'products/checkout.html', {
        'form': form,
        'items': items,
        'total': total,
    })


@csrf_exempt
def temporary_admin_setup(request):
    # Only allow POST requests.
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    # Require the private token stored in Render.
    expected_token = os.environ.get("LIVE_ADMIN_SETUP_TOKEN", "")
    provided_token = request.headers.get("X-Admin-Setup-Token", "")

    if not expected_token or not hmac.compare_digest(
        provided_token, expected_token
    ):
        return HttpResponse("Forbidden", status=403)

    User = get_user_model()

    # Create the admin only if no superuser exists yet.
    if User.objects.filter(is_superuser=True).exists():
        return HttpResponse("Admin setup already completed.", status=409)

    username = request.headers.get("X-Admin-Username", "")
    password = request.headers.get("X-Admin-Password", "")

    if not username or not password or len(password) < 12:
        return HttpResponse(
            "Provide a username and a password of at least 12 characters.",
            status=400,
        )

    if User.objects.filter(username=username).exists():
        return HttpResponse("That username already exists.", status=409)

    User.objects.create_superuser(
        username=username,
        email="",
        password=password,
    )

    return HttpResponse("Admin created. Remove this temporary endpoint now.")
