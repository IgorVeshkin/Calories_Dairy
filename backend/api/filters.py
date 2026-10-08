import django_filters

from .models import DayDairy

from django import forms


class DayDairyFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(
        field_name="create_date",
        lookup_expr="date__gte",
        label="Начальная Дата",
        widget=forms.DateInput(
            attrs={"type": "date"},
            format="%d-%m-%Y",
        ),
    )

    date_to = django_filters.DateFilter(
        field_name="create_date",
        lookup_expr="date__lte",
        label="Конечная Дата",
        widget=forms.DateInput(
            attrs={"type": "date"},
            format="%d-%m-%Y",
        ),
    )

    class Meta:
        model = DayDairy
        fields = []