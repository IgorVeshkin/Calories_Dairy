import django_filters

from .models import DayDairy

from django import forms

from rest_framework.filters import OrderingFilter


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


class FoodEntityOrderingFilter(OrderingFilter):

    def get_template_context(self, request, queryset, view):
        
        current = self.get_ordering(request, queryset, view)
        current = None if current is None else current[0]

        options = []

        for key, label in self.get_valid_fields(
            queryset,
            view,
            {"request": request}
        ):
            options.append(
                (key, f"{label} - по возрастанию")
            )

            options.append(
                (f"-{key}", f"{label} - по убыванию")
            )

        return {
            "request": request,
            "current": current,
            "param": self.ordering_param,
            "options": options,
        }