import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from api.models import FoodEntity, FoodRecord, DayDairy

from io import BytesIO
from PIL import Image

import random


def form_test_food_image(img_name="test_food.jpg"):
    
    buffer = BytesIO()

    Image.new("RGB", (100, 100), color="red").save(
        buffer,
        format="JPEG",
    )
    
    return SimpleUploadedFile(
        name=img_name,
        content=buffer.getvalue(),
        content_type="image/jpeg",
    )


def food_entities_search_by_name(records, name):

    return next(
        food_entity for food_entity in records
        if name.lower() in food_entity.name.lower()
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_user(db):
    
    # Создание записи пользователя и авторизация
    User = get_user_model() 

    return User.objects.create_user(
        username="Igor",
        password="test-password-1234",
    )


@pytest.fixture
def food_entities_list(db, auth_user):
    return FoodEntity.objects.bulk_create([
        FoodEntity(
            name="Овсянные хлопья",
            description="Бренд 'Myllyn Paras'. Коробка 500 грамм",
            image=form_test_food_image("oatmeal_porridge.jpg"),

            proteins=12,
            fats=6,
            carbs=62,
            fibers=6,
            calories=350,

            creator=auth_user,
        ),

        FoodEntity(
            name="Фарш куриный",
            description="Бренд 'Петелинка'. Лоток 450 грамм",
            image=form_test_food_image("grounded_chicken.jpg"),

            proteins=20,
            fats=5,
            carbs=0,
            fibers=0,
            calories=130,

            creator=auth_user,
        ),

        FoodEntity(
            name="Гречка хлопья",
            description="Бренд 'Селяночка'. Хлопья быстрого приготовления 1-3 минуты",
            image=form_test_food_image("buckwheat_flakes.jpg"),

            proteins=20,
            fats=5,
            carbs=0,
            fibers=0,
            calories=130,

            creator=auth_user,
        ),

        FoodEntity(
            name="Молоко 3.2% гост",
            description="Молоко ГОСТ. 1.6 литр в бутылке",
            image=form_test_food_image("milk.jpg"),

            proteins=3,
            fats=3.2,
            carbs=4.7,
            fibers=0,
            calories=60,

            creator=auth_user,
        ),

        FoodEntity(
            name="Сыр легкий",
            description="Сыр полутвердый 'Стародубский'. Легкий весовой сыр",
            image=form_test_food_image("cheese_light.jpg"),

            proteins=28.5,
            fats=13.5,
            carbs=0,
            fibers=0,
            calories=236,

            creator=auth_user,
        ),

        FoodEntity(
            name="Соус Терияки",
            description="Бренд 'Махеев'",
            image=form_test_food_image("teriyaki_sauce.jpg"),

            proteins=0.5,
            fats=0,
            carbs=43,
            fibers=0,
            calories=174,

            creator=auth_user,
        ),
    ])


@pytest.fixture
def day_dairy(db, auth_user):
    return DayDairy.objects.create(
        title="Суточное потребление 03.11.2026",
        description="Дневник за 3 ноября. Раннем утром поел в районе, утром был уже в городе",

        owner=auth_user,
    )


@pytest.fixture
def food_record(db, food_entities_list, day_dairy):

    souce_record = food_entities_search_by_name(food_entities_list, "соус")

    return FoodRecord.objects.create(
        food_base=souce_record,
        grams=40.0,
        day_dairy=day_dairy,
    )



@pytest.fixture
def food_records_list(db, food_entities_list, day_dairy):
    
    food_records = []

    for record in food_entities_list:
        food_records.append(
            FoodRecord(
                food_base=record,
                grams=random.randint(40, 150),
                day_dairy=day_dairy,
            )
        )

    
    return FoodRecord.objects.bulk_create(food_records)


@pytest.mark.django_db
def test_food_record_auth_check(api_client):

    """
    Проверка авторизации GET-запроса для модели FoodRecord
    """

    url = reverse("food-records-list")
    response = api_client.get(url)


    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_food_record_list(api_client, auth_user, food_record):

    """
    Проверка GET-запроса для модели FoodRecord
    """

    api_client.force_login(auth_user)


    # Проверка /api/food-records/ (если используется Router, тогда "basename"-list)
    url = reverse("food-records-list")
    response = api_client.get(url)


    received_data = response.data["results"]

    # Базовая проверка
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list) or "results" in response.data
    assert len(received_data) != 0

    # Проверка: входят ли определенные ключи в результат запроса и не пустые ли они
    for food_record in received_data:
        assert "grams" in food_record
        assert food_record["food_base"] is not None
        assert food_record["day_dairy"] is not None


@pytest.mark.django_db
def test_food_record_specific(api_client, auth_user, food_record):

    """
    Проверка GET-запроса для определенной записи модели FoodRecord
    """

    api_client.force_login(auth_user)


    # Проверка /api/food-records/<uuid> (если используется Router, тогда "basename"-detail)
    url = reverse("food-records-detail", kwargs={"pk": food_record.uuid},)
    response = api_client.get(url)

    received_record = response.data


    # Базовая проверка
    assert response.status_code == status.HTTP_200_OK


    db_record = FoodRecord.objects.get(
        uuid=received_record.get("uuid")
    )

    assert received_record["food_name"] == db_record.food_base.name

    assert received_record["food_base"] == db_record.food_base.pk
    assert received_record["day_dairy"] == db_record.day_dairy.pk

    assert float(received_record["grams"]) == float(db_record.grams)


@pytest.mark.django_db
def test_create_food_record(api_client, auth_user, food_entities_list, day_dairy):
    
    """
    Проверка POST-запроса для модели FoodRecord
    """
    
    # Авторизация пользователя
    api_client.force_login(auth_user)


    ground_chicken = food_entities_search_by_name(food_entities_list, "фарш")

    payload = {
        "food_base": ground_chicken.pk,
        "grams": 200,
        "day_dairy": day_dairy.pk,
    }


    # Создание новой записи через POST-запрос
    url = reverse("food-records-list")

    response = api_client.post(url, payload, format="json")

    
    # Проверки POST-запроса и созданой записи
    assert response.status_code == 201


    received_data = response.data

    assert FoodRecord.objects.filter(
        food_base=ground_chicken.uuid,
    ).exists()


    created_record = FoodRecord.objects.get(
        uuid=received_data.get("uuid")
    )

    assert float(received_data["grams"]) == float(created_record.grams)

    assert received_data["food_base"] == created_record.food_base.pk
    assert received_data["day_dairy"] == created_record.day_dairy.pk


@pytest.mark.django_db
def test_full_update_food_record(api_client, auth_user, food_records_list, food_entities_list, day_dairy):
    
    """
    Проверка PUT-запроса для модели FoodRecord
    """
    
    # Авторизация пользователя
    api_client.force_login(auth_user)


    random_food_record = random.choice(food_records_list)

    random_food_entity = random.choice(
        [
            specific_entity for specific_entity in food_entities_list 
            if specific_entity.uuid != random_food_record.food_base.pk
        ]
    )

    payload = {
        "food_base": random_food_entity.pk,
        "grams": random_food_record.grams + random.randint(10, 20),
        "day_dairy": day_dairy.pk,
    }


    # Полное обновление записи через PUT-запрос
    url = reverse("food-records-detail", kwargs={"pk": random_food_record.uuid},)

    response = api_client.put(url, payload, format="json")


    received_data = response.data

    assert FoodRecord.objects.filter(
        uuid=received_data["uuid"],
    ).exists()


    # Проверки PUT-запроса
    assert response.status_code == status.HTTP_200_OK


    assert received_data["day_dairy"] == random_food_record.day_dairy.pk
    assert received_data["food_base"] != random_food_record.food_base.pk

    assert float(received_data["grams"]) != float(random_food_record.grams)


@pytest.mark.django_db
def test_partial_update_food_record(api_client, auth_user, food_records_list):
    
    """
    Проверка PATCH-запроса для модели FoodRecord
    """
    
    # Авторизация пользователя
    api_client.force_login(auth_user)


    random_food_record = random.choice(food_records_list)
    random_grams_increase = random.randint(10, 20)


    payload = {
        "grams": random_food_record.grams + random_grams_increase,
    }


    # Полное обновление записи через PUT-запрос
    url = reverse("food-records-detail", kwargs={"pk": random_food_record.uuid},)

    response = api_client.patch(url, payload, format="json")

    received_data = response.data


    # Прогон тестов
    assert response.status_code == status.HTTP_200_OK

    assert float(received_data["grams"]) != float(random_food_record.grams)
    assert float(received_data["grams"]) == float(random_food_record.grams + random_grams_increase)


@pytest.mark.django_db
def test_delete_food_record(api_client, auth_user, food_records_list, food_record):
    
    """
    Проверка DELETE-запроса для модели FoodRecord
    """
    
    # Авторизация пользователя
    api_client.force_login(auth_user)


    # Удаление записи через DELETE-запрос
    url = reverse("food-records-detail", kwargs={"pk": food_record.uuid},)

    response = api_client.delete(url)


    assert response.status_code == 204
    assert not FoodRecord.objects.filter(pk=food_record.pk).exists()


@pytest.mark.django_db
def test_searching_food_record(api_client, auth_user, food_records_list):
    
    """
    Проверка поиска по списку записей для модели FoodRecord
    """
    
    # Авторизация пользователя
    api_client.force_login(auth_user)


    search_query = "хлопья"

    # Проверка /api/food-records/ с примененым поиском
    url = reverse("food-records-list")
    response = api_client.get(
        url, 
        {"search": search_query},
    )


    assert response.status_code == status.HTTP_200_OK


    # Поиск записей локально
    filtered_food_records_list = [
        food_record.food_base.name 
        for food_record in food_records_list
        if any(
            search_query.lower() in getattr(food_record.food_base, field).lower() 
            for field in ["name", "description"]
        )
    ]


    # Поиск через api
    results = response.data.get("results", response.data)
    results_names = [f_record["food_name"] for f_record in results]

    assert len(results_names) == len(filtered_food_records_list)
    assert sorted(results_names) == sorted(filtered_food_records_list)


@pytest.mark.django_db
def test_ordering_food_record(api_client, auth_user, food_records_list):

    """
    Проверка сортировки (по названию) списка записей для модели FoodRecord
    """
    
    # Авторизация пользователя
    api_client.force_login(auth_user)


    # Проверка /api/food-records/ с примененой сортировкой
    url = reverse("food-records-list")
    response = api_client.get(
        url, 
        {"ordering": "food_base__name"},
    )

    assert response.status_code == status.HTTP_200_OK


    results = response.data.get("results", response.data)

    # Отсортированные через api названия продуктов
    ordered_by_name_api_result = [f_record["food_name"] for f_record in results]

    # Отсортированные через Python записи из базы данных
    ordered_by_name_food_records_list = sorted([f_record.food_base.name for f_record in food_records_list])
    
    assert ordered_by_name_api_result == ordered_by_name_food_records_list