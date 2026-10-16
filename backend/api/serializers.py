from rest_framework import serializers

from django.contrib.auth.models import User

from .models import DayDairy, FoodEntity, FoodRecord


class DayDairySerializer(serializers.ModelSerializer):

    total_proteins = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    total_fats = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    total_carbs = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    total_fibers = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    total_calories = serializers.DecimalField(
        max_digits=10,
        decimal_places=1,
        read_only=True
    )
    
    class Meta:
        model = DayDairy
        fields = (
            'uuid',
            'title', 
            'description', 
            'total_proteins', 
            'total_fats', 
            'total_carbs', 
            'total_fibers',
            'total_calories',
        )


class FoodCreatorSerializer(serializers.ModelSerializer):

    class Meta:

        model = User

        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
        )


class FoodEntitySerializer(serializers.ModelSerializer):

    creator = FoodCreatorSerializer(read_only=True)

    image = serializers.ImageField(
        required=False
    )

    create_date = serializers.DateTimeField(
        format="%d.%m.%Y %H:%M:%S",
        read_only=True
    )

    update_date = serializers.DateTimeField(
        format="%d.%m.%Y %H:%M:%S",
        read_only=True
    )

    class Meta:
        model = FoodEntity

        fields = (
            "uuid",
            "name",
            "description",
            "image",
            "proteins",
            "fats",
            "carbs",
            "fibers",
            "calories",
            "creator",
            "create_date",
            "update_date",
        )

        read_only_fields = (
            "uuid",
            "creator",
            "create_date",
            "update_date",
        )



class FoodRecordSerializer(serializers.ModelSerializer):
    
    food_name = serializers.CharField(
        source="food_base.name",
        read_only=True
    )

    create_date = serializers.DateTimeField(
        format="%d.%m.%Y %H:%M:%S",
        read_only=True
    )


    total_proteins = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    total_fats = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    total_carbs = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    total_fibers = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    total_calories = serializers.DecimalField(
        max_digits=10,
        decimal_places=1,
        read_only=True
    )

    class Meta:
        model = FoodRecord

        fields = (
            "uuid",
            "create_date",
            "food_name",

            "food_base",
            "grams",
            "day_dairy",

            "total_proteins",
            "total_fats",
            "total_carbs",
            "total_fibers",
            "total_calories",
        )

        read_only_fields = (
            "uuid",
            "create_date",
            "food_name",
        )