# main/models.py

from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название товара")
    name_en = models.CharField(max_length=200, blank=True, null=True, verbose_name="Название товара (англ.)")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name="Категория")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Изображение товара")
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['name']

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название ингредиента")
    description = models.TextField(blank=True, verbose_name="Описание ингредиента")
    unit = models.CharField(max_length=50, verbose_name="Единица измерения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ['name']

    def __str__(self):
        return self.name

class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name="Ингредиент")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Количество")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    class Meta:
        unique_together = ('product', 'ingredient')
        verbose_name = "Состав товара"
        verbose_name_plural = "Состав товаров"
        ordering = ['product', 'ingredient']

    def __str__(self):
        return f"{self.product.name} - {self.ingredient.name}"

class Customer(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Номер телефона")
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders', verbose_name="Покупатель")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма")
    is_completed = models.BooleanField(default=False, verbose_name="Заказ завершен")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-order_date']

    def __str__(self):
        return f"Заказ #{self.id} от {self.customer.first_name} {self.customer.last_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления в заказ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"
        ordering = ['order', 'product']

    def __str__(self):
        return f"{self.product.name} x {self.quantity} в заказе {self.order.id}"

class FavoriteProduct(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='favorite_products', verbose_name="Покупатель")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления в избранное")

    class Meta:
        unique_together = ('customer', 'product')
        verbose_name = "Избранный товар"
        verbose_name_plural = "Избранные товары"
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.customer.first_name} - {self.product.name} (Избранное)"