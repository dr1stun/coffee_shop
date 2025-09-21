from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Sum, F
from .models import Product, Category, Customer, FavoriteProduct
from .forms import ProductForm
from django.contrib import messages
from django.db.models import Q


def home_page(request):
    featured_products = Product.objects.filter(is_available=True)[:4]
    categories = Category.objects.all()


    popular_products = Product.objects.annotate(total_ordered_quantity=Sum('orderitem__quantity')).filter(
        is_available=True,total_ordered_quantity__isnull=False).order_by('-total_ordered_quantity')[:5]

    new_products = Product.objects.filter(is_available=True).order_by('-created_at')[:5]


    top_customers = Customer.objects.annotate(order_count=Count('orders')).order_by('-order_count')[:3]

    context = {
        'featured_products': featured_products,
        'categories': categories,
        'popular_products': popular_products,
        'new_products': new_products,
        'top_customers': top_customers,
        'categories_count': Category.objects.count(),
        'all_products_count': Product.objects.count(),
        'available_products_count': Product.objects.filter(is_available=True).count(),
    }
    return render(request, 'main/home.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    ingredients = product.productingredient_set.all()

    is_favorite = False
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(email=request.user.email) # Пример создания/получения Customer из User
        is_favorite = FavoriteProduct.objects.filter(customer=customer, product=product).exists()
    return render(request, 'main/product_detail.html', {'product': product, 'ingredients': ingredients, 'is_favorite': is_favorite})

def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно добавлен!')
            return redirect('home')
    else:
        form = ProductForm()
    return render(request, 'main/product_form.html', {'form': form, 'title': 'Добавить новый товар'})

def product_edit(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Информация о товаре успешно обновлена!')
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'main/product_form.html', {'form': form, 'product': product, 'title': f'Редактировать товар: {product.name}'})

def product_delete(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар успешно удален!')
        return redirect('home')
    return render(request, 'main/product_confirm_delete.html', {'product': product})

def search_results(request):
    query = request.GET.get('q')
    products = Product.objects.all()
    if query:
        # Поиск по названию товара, описанию или категории
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct() # distinct() для избежания дубликатов при поиске по нескольким поля #

    return render(request, 'main/search_results.html', {'products': products, 'query': query})

def add_to_favorites(request, product_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Пожалуйста, войдите в систему, чтобы добавить в избранное.')
            return redirect('product_detail', product_id=product_id)

        product = get_object_or_404(Product, pk=product_id)
        customer, created = Customer.objects.get_or_create(email=request.user.email, defaults={'first_name': request.user.username, 'last_name': 'Пользователь'})

        favorite, created = FavoriteProduct.objects.get_or_create(customer=customer, product=product)
        if created:
            messages.success(request, f'Товар "{product.name}" добавлен в избранное.')
        else:
            messages.info(request, f'Товар "{product.name}" уже был в избранном.')
        return redirect('product_detail', product_id=product_id)
    return redirect('home')