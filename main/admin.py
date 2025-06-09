# main/admin.py

from django.contrib import admin
from .models import Category, Product, Ingredient, ProductIngredient, Customer, Order, OrderItem, FavoriteProduct
from django.utils.html import format_html # Для использования собственного метода в list_display

# Inlines для связанных моделей
class ProductIngredientInline(admin.TabularInline):
    model = ProductIngredient
    extra = 1 # Количество пустых форм для добавления
    raw_id_fields = ('ingredient',) # Удобный виджет для выбора связанных объектов

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    raw_id_fields = ('product',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'product_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at' # Иерархия по дате
    readonly_fields = ('created_at', 'updated_at') # Поля только для чтения

    @admin.display(description='Количество товаров') # short_description для собственного метода
    def product_count(self, obj):
        return obj.products.count()

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'display_image_thumbnail', 'created_at', 'updated_at')
    list_display_links = ('name',) # Поле, которое будет ссылкой на страницу редактирования
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    raw_id_fields = ('category',) # Удобный виджет для выбора внешних ключей
    date_hierarchy = 'created_at'
    inlines = [ProductIngredientInline] # Встраиваем inline для ProductIngredient
    readonly_fields = ('created_at', 'updated_at', 'display_image_thumbnail') # Добавляем превью изображения в readonly
    filter_horizontal = () # Здесь не используется, так как у нас нет ManyToMany без промежуточной модели

    @admin.display(description='Миниатюра')
    def display_image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: contain;" />', obj.image.url)
        return "Нет изображения"

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'created_at', 'updated_at')
    list_filter = ('unit', 'created_at')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ProductIngredient)
class ProductIngredientAdmin(admin.ModelAdmin):
    list_display = ('product', 'ingredient', 'quantity', 'created_at')
    list_filter = ('product', 'ingredient')
    search_fields = ('product__name', 'ingredient__name')
    raw_id_fields = ('product', 'ingredient') # Удобный виджет
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'registered_at', 'updated_at')
    list_display_links = ('first_name', 'last_name')
    list_filter = ('registered_at',)
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    date_hierarchy = 'registered_at'
    readonly_fields = ('registered_at', 'updated_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'total_amount', 'is_completed', 'updated_at')
    list_display_links = ('id',)
    list_filter = ('is_completed', 'order_date')
    search_fields = ('customer__first_name', 'customer__last_name', 'id')
    date_hierarchy = 'order_date'
    inlines = [OrderItemInline] # Встраиваем inline для OrderItem
    readonly_fields = ('order_date', 'updated_at', 'total_amount') # total_amount будет рассчитываться автоматически

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # При сохранении заказа, пересчитываем total_amount
        total = sum(item.quantity * item.price for item in obj.items.all())
        if obj.total_amount != total:
            obj.total_amount = total
            obj.save(update_fields=['total_amount'])

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'created_at')
    list_filter = ('order', 'product')
    search_fields = ('order__id', 'product__name')
    raw_id_fields = ('order', 'product')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'added_at')
    list_filter = ('customer', 'product', 'added_at')
    search_fields = ('customer__first_name', 'customer__last_name', 'product__name')
    raw_id_fields = ('customer', 'product')
    readonly_fields = ('added_at',)