from rest_framework.response import Response

from .models import DayDairy, FoodEntity, FoodRecord
from .serializers import DayDairySerializer, FoodEntitySerializer, FoodRecordSerializer
from .filters import DayDairyFilter, FoodEntityOrderingFilter
from .paginations import DayDairyPagination, FoodModelsPagination

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend

from django.utils import timezone
from datetime import timedelta
from django.utils.dateparse import parse_date


from decimal import Decimal

from django.db.models import (
    Sum,
    F,
    Value,
    DecimalField,
    ExpressionWrapper,
)

from django.db.models.functions import Coalesce


# Create your views here.


# Функция подсчета всех нутриентов за день
def nutrient_expression(field):
    expression = ExpressionWrapper(
        F(f"food_day_dairy__food_base__{field}")
        * F("food_day_dairy__grams")
        / Value(Decimal("100")),
        output_field=DecimalField(
            max_digits=10,
            decimal_places=2
        ),
    )

    return Coalesce(
        Sum(expression),
        Value(Decimal("0.00")),
        output_field=DecimalField(
            max_digits=10,
            decimal_places=2
        ),
    )


def get_nutrient(field):
    return ExpressionWrapper(
        F("grams")
        * F(f"food_base__{field}")
        / Value(Decimal("100")),
        output_field=DecimalField(
            max_digits=10,
            decimal_places=2,
        )
    )


class DayDairyViewSet(ModelViewSet):
    serializer_class = DayDairySerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_class = DayDairyFilter

    pagination_class = DayDairyPagination


    # Получение данных
    def get_queryset(self):
        queryset = DayDairy.objects.filter(
            owner=self.request.user,
        ).order_by('-create_date')

        # Применение новых высчитанных полей (белок, калории, клетчатка и т.д.)
        queryset = queryset.annotate(
            total_proteins=nutrient_expression("proteins"),
            total_fats=nutrient_expression("fats"),
            total_carbs=nutrient_expression("carbs"),
            total_fibers=nutrient_expression("fibers"),
            total_calories=nutrient_expression("calories"),
        )

        # Получение данных по датам (используется кастомный фильтр)
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        
        # Загрузка данных за неделю, если другой период неизвестен
        if not date_from and not date_to:
            today = timezone.localdate()
            week_age = today - timedelta(days=7)

            queryset = queryset.filter(
                create_date__date__range=(week_age, today)  
            )

        return queryset

    # Переписываю поведение сохранения модели
    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user
        )

    
    # Информационная плашка для дат предоставляемых данных
    def get_view_description(self, html=False):
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")


        if not date_from and not date_to:
            today = timezone.localdate()
            date_from = today - timedelta(days=7)
            date_to = today


        if isinstance(date_from, str):
            date_from = parse_date(date_from)


        if isinstance(date_to, str):
            date_to = parse_date(date_to)


        if date_from and date_to:
            return "Период: {} - {}".format(
                date_from.strftime("%d.%m.%Y"),
                date_to.strftime("%d.%m.%Y"),
            )


        if date_from:
            return "Период: с {}".format(
                date_from.strftime("%d.%m.%Y")
            )


        if date_to:
            return "Период: до {}".format(
                date_to.strftime("%d.%m.%Y")
            )

        return "Период не указан"


class FoodEntityViewSet(ModelViewSet):
    serializer_class = FoodEntitySerializer
    permission_classes = [IsAuthenticated]

    pagination_class = FoodModelsPagination

    parser_classes = (
        MultiPartParser,
        FormParser,
        JSONParser,
    )

    filter_backends = (
        SearchFilter,
        FoodEntityOrderingFilter,
    )

    search_fields = (
        "name",
        "description",
    )

    ordering_fields = (
        ("name", "Название"),
        ("calories", "Калории"),
        ("proteins", "Белок"),
        ("fats", "Жиры"),
        ("carbs", "Углеводы"),
        ("create_date", "Дата создания"),
    )

    ordering = ("-create_date",)

    def get_queryset(self):
        return FoodEntity.objects.filter(
            creator=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            creator=self.request.user
        )


class FoodRecordViewSet(ModelViewSet):
    serializer_class = FoodRecordSerializer
    permission_classes = [IsAuthenticated]

    pagination_class = FoodModelsPagination

    parser_classes = (
        MultiPartParser,
        FormParser,
        JSONParser,
    )

    filter_backends = (
        SearchFilter,
        FoodEntityOrderingFilter,
    )

    search_fields = (
        "name",
        "description",
    )

    ordering_fields = (
        ("name", "Название"),
        ("calories", "Калории"),
        ("proteins", "Белок"),
        ("fats", "Жиры"),
        ("carbs", "Углеводы"),
        ("create_date", "Дата создания"),
    )

    ordering = ("-create_date",)


    def get_queryset(self):
        user_food_record = FoodRecord.objects.filter(
            day_dairy__owner=self.request.user
        )

        return (
            user_food_record
            .select_related("food_base")
            .annotate(
                total_proteins=get_nutrient("proteins"),
                total_fats=get_nutrient("fats"),
                total_carbs=get_nutrient("carbs"),
                total_fibers=get_nutrient("fibers"),
                total_calories=get_nutrient("calories"),
            )
        )