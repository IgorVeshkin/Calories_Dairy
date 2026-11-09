import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from api.models import FoodEntity, FoodRecord, DayDairy

from io import BytesIO
from PIL import Image

from django.forms.models import model_to_dict
from decimal import Decimal


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
def food_entity(db, auth_user):
    return FoodEntity.objects.create(
        name="Овсянные хлопья",
        description="Бренд 'Myllyn Paras'. Коробка 500 грамм",
        image=form_test_food_image("oatmeal_porridge.jpg"),

        proteins=12,
        fats=6,
        carbs=62,
        fibers=6,
        calories=350,

        creator=auth_user,
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


@pytest.mark.django_db
def test_food_entities_auth_check(api_client):

    """
    Проверка авторизации GET-запроса для модели FoodEntity
    """

    url = reverse("foods-list")
    response = api_client.get(url)


    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_food_entities_list(api_client, auth_user):

    """
    Проверка GET-запроса для модели FoodEntity
    """

    api_client.force_login(auth_user)


    # Проверка /api/foods/ (если используется Router, тогда "basename"-list)
    url = reverse("foods-list")
    response = api_client.get(url)


    # Базовая проверка
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list) or "results" in response.data


@pytest.mark.django_db
def test_food_entity_specific(api_client, auth_user, food_entity):

    """
    Проверка GET-запроса для определенной записи модели FoodEntity
    """

    api_client.force_login(auth_user)


    # Проверка /api/foods/<uuid> (если используется Router, тогда "basename"-detail)
    url = reverse("foods-detail", kwargs={"pk": food_entity.uuid},)
    response = api_client.get(url)

    received_record = response.data


    # Базовая проверка
    assert response.status_code == status.HTTP_200_OK


    db_record = FoodEntity.objects.get(
        uuid=received_record.get("uuid")
    )

    assert received_record["name"] == db_record.name

    assert received_record["uuid"] == str(db_record.uuid)
    assert received_record["creator"]["id"] == db_record.creator.pk

    assert float(received_record["calories"]) == float(db_record.calories)


@pytest.mark.django_db
def test_create_food_entities(api_client, auth_user):

    """
    Проверка POST-запроса для модели FoodEntity
    """
    
    # Авторизация пользователя
    api_client.force_login(auth_user)


    # Формирование json и изображения для POST-запроса    
    food_image = form_test_food_image("ground_chicken.jpg")

    payload = {
        "name":'Фарш куриный',
        "description":'Бренд "Петелинка"',
        "image":food_image,

        "proteins":20,
        "fats":5,
        "carbs":1.5,
        "fibers":0,
        "calories":130,

        "creator": auth_user.pk,
    }


    # Создание новой записи через POST-запрос
    url = reverse("foods-list")

    response = api_client.post(url, payload, format="multipart")

    
    # Проверки POST-запроса и созданой записи продукта
    assert response.status_code == 201
    assert FoodEntity.objects.filter(
        name='Фарш куриный',
    ).exists()
    assert FoodEntity.objects.get(
        uuid=response.data.get("uuid")
    ).creator == auth_user


@pytest.mark.django_db
def test_partial_update_food_entities(api_client, auth_user, food_entity):

    """
    Проверка PATCH-запроса для модели FoodEntity
    """

    api_client.force_login(auth_user)

    food_entity_backup = model_to_dict(food_entity)


    payload = {
        "proteins": 14,
        "calories": 358,
    }

    # Проверка PATCH /api/foods/<uuid>
    url = reverse("foods-detail", kwargs={"pk": food_entity.uuid},)
    response = api_client.patch(
        url, 
        payload,
        format="json",
    )


    # Прогон тестов
    assert response.status_code == status.HTTP_200_OK
    assert response.data["proteins"] != food_entity_backup["proteins"]
    assert response.data["calories"] != food_entity_backup["calories"]


@pytest.mark.django_db
def test_full_update_food_entities(api_client, auth_user, food_entity):

    """
    Проверка PUT-запроса для модели FoodEntity
    """
    
    # Авторизация пользователя
    api_client.force_login(auth_user)

    food_entity_backup = model_to_dict(food_entity)


    # Формирование json и изображения для PUT-запроса
    food_image = form_test_food_image("ground_chicken.jpg")

    payload = {
        "name":'Овсянные хлопья updated',
        "description":'Бренд "Myllyn Paras". Коробка 500 грамм. Тестовый текст',
        "image":food_image,

        "proteins":14,
        "fats":7,
        "carbs":62,
        "fibers":6,
        "calories":350,

        "creator": auth_user.pk,
    }


    # Полное обновление записи через PUT-запрос
    url = reverse("foods-detail", kwargs={"pk": food_entity.uuid},)

    response = api_client.put(url, payload, format="multipart")


    # Проверки PUT-запроса и изменений в записи продукта
    assert response.status_code == status.HTTP_200_OK

    assert response.data["name"] != food_entity_backup["name"]
    assert response.data["description"] != food_entity_backup["description"]

    assert Decimal(response.data["proteins"]) != Decimal(food_entity_backup["proteins"])
    assert Decimal(response.data["fats"]) != Decimal(food_entity_backup["fats"])

    assert Decimal(response.data["carbs"]) == Decimal(food_entity_backup["carbs"])
    assert Decimal(response.data["fibers"]) == Decimal(food_entity_backup["fibers"])
    assert Decimal(response.data["calories"]) == Decimal(food_entity_backup["calories"])


@pytest.mark.django_db
def test_delete_food_entity(api_client, auth_user, food_entity):
    
    """
    Проверка DELETE-запроса для модели FoodEntity
    """
    
    # Авторизация пользователя
    api_client.force_login(auth_user)

    # Удаление записи через DELETE-запрос
    url = reverse("foods-detail", kwargs={"pk": food_entity.uuid},)

    response = api_client.delete(url)

    assert response.status_code == 204
    assert not FoodEntity.objects.filter(pk=food_entity.pk).exists()


@pytest.mark.django_db
def test_ordering_food_entity(api_client, auth_user, food_entities_list):

    """
    Проверка сортировки (по названию) списка записей для модели FoodEntity
    """
    
    # Авторизация пользователя
    api_client.force_login(auth_user)


    # Проверка /api/foods/ с примененой сортировкой
    url = reverse("foods-list")
    response = api_client.get(
        url, 
        {"ordering": "name"},
    )

    assert response.status_code == status.HTTP_200_OK

    results = response.data.get("results", response.data)


    # Отсортированные через api названия продуктов
    ordered_by_name_api_result = [food_entity["name"] for food_entity in results]

    # Отсортированные через Python записи из базы данных
    ordered_by_name_food_entities_list = sorted([food_entity.name for food_entity in food_entities_list])
    
    assert ordered_by_name_api_result == ordered_by_name_food_entities_list


@pytest.mark.django_db
def test_searching_food_entity(api_client, auth_user, food_entities_list):
    
    """
    Проверка поиска по списку записей для модели FoodEntity
    """
    
    # Авторизация пользователя
    api_client.force_login(auth_user)


    search_query = "хлопья"

    # Проверка /api/foods/ с примененым поиском
    url = reverse("foods-list")
    response = api_client.get(
        url, 
        {"search": search_query},
    )


    assert response.status_code == status.HTTP_200_OK
    

    # Поиск записей локально
    filtered_food_entities_list = [
        food_entity.name 
        for food_entity in food_entities_list 
        if any(
            search_query.lower() in getattr(food_entity, field).lower() 
            for field in ["name", "description"]
        )
    ]

    # Поиск через api
    results = response.data.get("results", response.data)
    results_names = [food_entity["name"] for food_entity in results]
    

    assert len(results_names) == len(filtered_food_entities_list)
    assert sorted(results_names) == sorted(filtered_food_entities_list)