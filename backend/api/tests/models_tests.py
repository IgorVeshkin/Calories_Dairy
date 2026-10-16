import pytest

from api.models import FoodEntity, FoodRecord, DayDairy

from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
def test_create_food_entity(django_user_model):

    user = django_user_model.objects.create_user(
        username="testuser",
        password="testpass123",
    )

    chicken_image = SimpleUploadedFile(
        name="apple.jpg",
        content=b"fake-image-content",
        content_type="image/jpeg",
    )

    ground_chicken = FoodEntity.objects.create(
        name="Фарш куриный",
        description="Фарш куриный 'Петелинка'",
        image=chicken_image,

        proteins=20,
        fats=5,
        carbs=0,
        fibers=0,
        calories=130,

        creator=user,
    )

    assert ground_chicken.pk is not None
    assert ground_chicken.name == "Фарш куриный"
    assert ground_chicken.calories == 130
    assert ground_chicken.creator == user
    assert ground_chicken.image.name.startswith(f"users/{user.pk}/foods/")


@pytest.mark.django_db
def test_create_day_dairy(django_user_model):

    user = django_user_model.objects.create_user(
        username="testuser",
        password="testpass123",
    )

    dairy = DayDairy.objects.create(
        title="Суточное потребление 16.10.2026",
        description="Тестовое описание дневника на день 16.10.2026",

        owner=user
    )

    assert dairy.pk is not None
    assert dairy.title.startswith("Суточное")
    assert dairy.owner == user


@pytest.mark.django_db
def test_create_food_record(django_user_model):

    user = django_user_model.objects.create_user(
        username="testuser",
        password="testpass123",
    )

    food_image = SimpleUploadedFile(
        name="apple.jpg",
        content=b"fake-image-content",
        content_type="image/jpeg",
    )

    food_entity = FoodEntity.objects.create(
        name="Фарш куриный",
        description="Фарш куриный 'Петелинка'",
        image=food_image,

        proteins=20,
        fats=5,
        carbs=0,
        fibers=0,
        calories=130,

        creator=user,
    )

    dairy = DayDairy.objects.create(
        title="Суточное потребление 16.10.2026",
        description="Тестовое описание дневника на день 16.10.2026",

        owner=user
    )


    food_record = FoodRecord.objects.create(
        food_base=food_entity,
        grams=242,
        day_dairy=dairy
    )

    
    assert food_record.pk is not None
    assert food_record.food_base.creator == food_record.day_dairy.owner

    assert food_entity.food_records.first().grams == food_record.grams
    