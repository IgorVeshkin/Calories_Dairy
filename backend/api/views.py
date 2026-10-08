from rest_framework.response import Response

from .models import DayDairy
from .serializers import DayDairySerializer
from .filters import DayDairyFilter
from .paginations import DayDairyPagination

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
        )

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