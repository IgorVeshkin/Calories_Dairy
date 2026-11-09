import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from api.models import FoodEntity, FoodRecord, DayDairy

import random

from django.forms.models import model_to_dict


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
def day_dairy_list(db, auth_user):
    return DayDairy.objects.bulk_create([
        DayDairy(
            title="Суточное потребление 01.11.2026",
            description="Дневник за 1 ноября. Находился в районе",

            owner=auth_user,
        ),

        DayDairy(
            title="Суточное потребление 02.11.2026",
            description="Дневник за 2 ноября. Находился в районе",

            owner=auth_user,
        ),

        DayDairy(
            title="Суточное потребление 03.11.2026",
            description="Дневник за 3 ноября. Раннем утром поел в районе, утром был уже в городе",

            owner=auth_user,
        ),

    ])


@pytest.fixture
def day_dairy(db, auth_user):
    return DayDairy.objects.create(
            title="Суточное потребление 06.11.2026",
            description="Дневник за 6 ноября. Находился в городе",

            owner=auth_user,
        )


@pytest.mark.django_db
def test_day_dairy_auth_check(api_client):

    """
    Проверка авторизации GET-запроса для модели DayDairy
    """

    url = reverse("dairy-list")
    response = api_client.get(url)


    assert response.status_code == status.HTTP_403_FORBIDDEN



@pytest.mark.django_db
def test_day_dairy_list(api_client, auth_user, day_dairy_list):

    """
    Проверка GET-запроса для модели DayDairy
    """

    api_client.force_login(auth_user)


    # Проверка /api/dairy/ (если используется Router, тогда "basename"-list)
    url = reverse("dairy-list")
    response = api_client.get(url)


    expected_keys = {"uuid", "title", "description"}

    # Базовая проверка
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list) or "results" in response.data
    assert len(response.data["results"]) != 0

    # Проверка: входят ли определенные ключи в результат запроса
    for item in response.data["results"]:
        assert expected_keys.issubset(item.keys())


@pytest.mark.django_db
def test_day_dairy_specific(api_client, auth_user, day_dairy_list):

    """
    Проверка GET-запроса для определенной записи модели DayDairy
    """

    api_client.force_login(auth_user)


    random_day_dairy_record = random.choice(day_dairy_list)

    # Проверка /api/dairy/<uuid> (если используется Router, тогда "basename"-detail)
    url = reverse("dairy-detail", kwargs={"pk": random_day_dairy_record.uuid},)
    response = api_client.get(url)

    received_record = response.data


    # Базовая проверка
    assert response.status_code == status.HTTP_200_OK
    assert len(received_record) != 0


    expected_keys = {"uuid", "title", "description"}

    # Проверка: входят ли определенные ключи в результат запроса
    assert expected_keys.issubset(received_record.keys())


    db_record = DayDairy.objects.get(
        uuid=received_record.get("uuid")
    )

    for key, value in received_record.items():

        db_record_value = getattr(db_record, key, None)

        if db_record_value is None:
            continue

        assert str(value) == str(db_record_value)


@pytest.mark.django_db
def test_create_day_dairy(api_client, auth_user, day_dairy_list):
    
    """
    Проверка POST-запроса для модели DayDairy
    """
    
    # Авторизация пользователя
    api_client.force_login(auth_user)


    payload = {
        "title": "Суточное потребление 06.11.2026",
        "description": "Дневник за 6 ноября. Находился в районе",
        
        "owner": auth_user.pk,
    }


    # Создание новой записи через POST-запрос
    url = reverse("dairy-list")

    response = api_client.post(url, payload, format="json")

    
    # Проверки POST-запроса и созданой записи
    assert response.status_code == 201


    received_data = response.data

    created_record = DayDairy.objects.get(
        uuid=received_data.get("uuid")
    )

    assert created_record is not None


    assert received_data["title"] == created_record.title
    assert received_data["description"] == created_record.description


@pytest.mark.django_db
def test_full_update_day_dairy(api_client, auth_user, day_dairy):

    """
    Проверка PUT-запроса для модели DayDairy
    """
    
    # Авторизация пользователя
    api_client.force_login(auth_user)


    day_dairy_backup = model_to_dict(day_dairy)


    payload = {
        "title": "Суточное потребление 06.11.2026 - Updated",
        "description": "Дневник за 6 ноября. Находился в районе. Стандартный день",
        
        "owner": auth_user.pk,
    }


    # Создание новой записи через PUT-запрос
    url = reverse("dairy-detail", kwargs={"pk": day_dairy.uuid},)

    response = api_client.put(url, payload, format="json")

    
    # Проверки PUT-запроса и созданой записи
    assert response.status_code == status.HTTP_200_OK


    received_data = response.data

    assert received_data["title"] != day_dairy_backup["title"]
    assert received_data["description"] != day_dairy_backup["description"]


@pytest.mark.django_db
def test_partial_update_day_dairy(api_client, auth_user, day_dairy):

    """
    Проверка PATCH-запроса для модели DayDairy
    """
    
    # Авторизация пользователя
    api_client.force_login(auth_user)


    day_dairy_backup = model_to_dict(day_dairy)


    payload = {
        "title": "Суточное потребление 06.11.2026 - Updated (1)",
    }


    # Создание новой записи через PATCH-запрос
    url = reverse("dairy-detail", kwargs={"pk": day_dairy.uuid},)

    response = api_client.patch(url, payload, format="json")

    
    # Проверки PUT-запроса и созданой записи
    assert response.status_code == status.HTTP_200_OK


    received_data = response.data

    assert received_data["title"] != day_dairy_backup["title"]
    assert received_data["description"] == day_dairy_backup["description"]


    db_record = DayDairy.objects.get(
        uuid=received_data.get("uuid")
    )

    # Сравнение данных до изменения и новых данных из бд
    assert db_record.title != day_dairy_backup["title"]
    assert db_record.description == day_dairy_backup["description"]


@pytest.mark.django_db
def test_delete_day_dairy(api_client, auth_user, day_dairy):
    
    """
    Проверка DELETE-запроса для модели DayDairy
    """
    
    # Авторизация пользователя
    api_client.force_login(auth_user)


    # Удаление записи через DELETE-запрос
    url = reverse("dairy-detail", kwargs={"pk": day_dairy.uuid},)

    response = api_client.delete(url)
    

    assert response.status_code == 204
    assert not DayDairy.objects.filter(pk=day_dairy.pk).exists()