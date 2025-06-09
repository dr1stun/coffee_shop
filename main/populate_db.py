# main/populate_db.py

import os
import django
from datetime import datetime, timedelta
import random

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coffee_shop.settings')
django.setup()

from django.core.files import File  # Для работы с изображениями
from django.db.models import Sum  # Для агрегации
from django.utils import timezone

from main.models import Category, Product, Ingredient, ProductIngredient, Customer, Order, OrderItem, FavoriteProduct


def populate_database(num_categories=5, num_ingredients=15, num_products=30, num_customers=10, num_orders=20):
    """
    Заполняет базу данных случайными данными для тестирования.
    """
    print("Начинаем заполнение базы данных...")

    # Удаляем существующие данные, чтобы избежать дубликатов при повторном запуске
    print("Очищаем существующие данные...")
    FavoriteProduct.objects.all().delete()
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    ProductIngredient.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    Ingredient.objects.all().delete()
    Customer.objects.all().delete()
    print("Данные очищены.")

    # --- 1. Заполнение Categories ---
    print(f"Создаем {num_categories} категорий...")
    categories = []
    category_names = ["Кофе", "Выпечка", "Десерты", "Напитки", "Снеки", "Сэндвичи", "Салаты", "Завтраки"]
    for i in range(num_categories):
        name = category_names[i % len(category_names)]
        description = f"Описание категории {name.lower()}."
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )
        categories.append(category)
        if created:
            print(f" - Создана категория: {category.name}")
    print("Категории созданы.")

    # --- 2. Заполнение Ingredients ---
    print(f"Создаем {num_ingredients} ингредиентов...")
    ingredients = []
    ingredient_data = [
        ("Кофейные зерна", "кг"), ("Молоко", "л"), ("Сахар", "кг"), ("Шоколад", "г"),
        ("Мука", "кг"), ("Яйца", "шт"), ("Сливочное масло", "г"), ("Фрукты", "г"),
        ("Ваниль", "г"), ("Вода", "л"), ("Взбитые сливки", "мл"), ("Лед", "шт"),
        ("Какао-порошок", "г"), ("Сироп", "мл"), ("Соль", "г")
    ]
    for i in range(num_ingredients):
        name, unit = ingredient_data[i % len(ingredient_data)]
        description = f"Качественный {name.lower()}."
        ingredient, created = Ingredient.objects.get_or_create(
            name=f"{name}_{i}",  # Добавляем индекс, чтобы имена были уникальными
            defaults={'description': description, 'unit': unit}
        )
        ingredients.append(ingredient)
        if created:
            print(f" - Создан ингредиент: {ingredient.name}")
    print("Ингредиенты созданы.")

    # --- 3. Заполнение Products ---
    print(f"Создаем {num_products} товаров...")
    products = []
    product_names = [
        "Эспрессо", "Капучино", "Латте", "Американо", "Флэт Уайт", "Мокко",
        "Круассан", "Пончик", "Маффин", "Чизкейк", "Тирамису", "Брауни",
        "Лимонад", "Апельсиновый сок", "Смузи", "Газированная вода", "Молочный коктейль",
        "Сэндвич с курицей", "Сэндвич с тунцом", "Овсяная каша", "Греческий салат",
        "Кофе без кофеина", "Горячий шоколад"
    ]
    for i in range(num_products):
        name = product_names[i % len(product_names)] + f" ({i + 1})"
        description = f"Восхитительный {name.lower()}."
        price = round(random.uniform(1.5, 7.5), 2)
        category = random.choice(categories)
        is_available = random.choice([True, True, True, False])

        product = Product(
            name=name,
            name_en=f"{name} (En)",
            description=description,
            price=price,
            category=category,
            is_available=is_available
        )

        # Для изображений: создаем фиктивный файл
        image_path = os.path.join(os.path.dirname(__file__), f"product_{i}.png")  # Изменил на .png, для ясности
        # Используем небольшой, валидный PNG 1x1 пиксель
        # Это бинарные данные минимального PNG файла.
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\xda\xed\xc1\x01\x01\x00\x00\x00\xc2\xa0\xf7Om\x00\x00\x00\x00IEND\xaeB`\x82'
        with open(image_path, 'wb') as f:
            f.write(png_data)

        product.image.save(f'product_images/product_{i}.png', File(open(image_path, 'rb')), save=False)
        os.remove(image_path)  # Удаляем временный файл

        product.save()
        products.append(product)
        print(f" - Создан товар: {product.name} (Категория: {product.category.name})")

        # Добавляем ингредиенты к товару (рандомно 1-3 уникальных ингредиента)
        # Получаем копию списка ингредиентов, чтобы можно было удалять из нее
        available_ingredients_for_product = list(ingredients)
        num_product_ingredients = random.randint(1, min(3, len(available_ingredients_for_product)))

        added_ingredients_for_this_product = set()  # Множество для отслеживания уже добавленных ингредиентов

        for _ in range(num_product_ingredients):
            if not available_ingredients_for_product:  # Если не осталось доступных ингредиентов
                break

            ingredient = random.choice(available_ingredients_for_product)

            # Убеждаемся, что этот ингредиент не был добавлен к этому продукту ранее в этой итерации
            if ingredient not in added_ingredients_for_this_product:
                quantity = round(random.uniform(0.01, 0.5), 2)
                ProductIngredient.objects.create(
                    product=product,
                    ingredient=ingredient,
                    quantity=quantity
                )
                added_ingredients_for_this_product.add(ingredient)
                available_ingredients_for_product.remove(ingredient)

    print("Товары и их состав созданы.")

    # --- 4. Заполнение Customers ---
    print(f"Создаем {num_customers} покупателей...")
    customers = []
    first_names = ["Александр", "Елена", "Дмитрий", "Ольга", "Иван", "Анна", "Сергей", "Наталья", "Михаил", "Татьяна"]
    last_names = ["Иванов", "Петрова", "Сидоров", "Кузнецова", "Смирнов", "Волкова", "Соколов", "Морозова", "Федоров",
                  "Новикова"]

    for i in range(num_customers):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
        phone_number = f"+79{random.randint(100000000, 999999999)}"

        customer, created = Customer.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'phone_number': phone_number
            }
        )
        customers.append(customer)
        if created:
            print(f" - Создан покупатель: {customer.first_name} {customer.last_name}")
    print("Покупатели созданы.")

    # --- 5. Заполнение Orders и OrderItems ---
    print(f"Создаем {num_orders} заказов...")
    min_date = timezone.now() - timedelta(days=90)  # Заказы за последние 90 дней
    for i in range(num_orders):
        customer = random.choice(customers)
        order_date = min_date + timedelta(days=random.randint(0, 90), hours=random.randint(0, 23),
                                          minutes=random.randint(0, 59))
        is_completed = random.choice([True, True, False])  # Чаще завершенные

        order = Order.objects.create(
            customer=customer,
            order_date=order_date,
            is_completed=is_completed,
            total_amount=0  # Будет пересчитана ниже
        )

        num_order_items = random.randint(1, 5)
        current_order_total = 0
        for _ in range(num_order_items):
            product = random.choice(products)
            quantity = random.randint(1, 3)
            price_at_order = product.price  # Используем текущую цену продукта

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price_at_order
            )
            current_order_total += quantity * float(price_at_order)

        order.total_amount = round(current_order_total, 2)
        order.save()
        print(f" - Создан заказ #{order.id} для {order.customer.first_name} (Сумма: {order.total_amount} €)")
    print("Заказы и элементы заказов созданы.")

    # --- 6. Заполнение FavoriteProducts ---
    print("Заполняем избранные товары...")
    num_favorites = random.randint(num_customers * 2, num_customers * 5)  # От 2 до 5 избранных на покупателя
    for _ in range(num_favorites):
        customer = random.choice(customers)
        product = random.choice(products)

        # Проверяем, существует ли уже эта запись, чтобы избежать UniqueConstraint
        if not FavoriteProduct.objects.filter(customer=customer, product=product).exists():
            FavoriteProduct.objects.create(
                customer=customer,
                product=product,
                added_at=timezone.now() - timedelta(days=random.randint(0, 60))
            )
            # print(f" - Добавлен в избранное: {customer.first_name} - {product.name}")
    print("Избранные товары заполнены.")

    print("\nЗаполнение базы данных завершено!")


if __name__ == '__main__':
    # Если вы запускаете этот файл напрямую: python main/populate_db.py
    populate_database()