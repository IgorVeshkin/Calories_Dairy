from django.contrib import admin

from .models import FoodEntity, FoodRecord, DayDairy
from django.core.exceptions import ValidationError

from django.utils import timezone
from django.utils.html import format_html
from django.utils.text import Truncator


from decimal import Decimal

from django.db.models import (
    Sum,
    F,
    Value,
    DecimalField,
    ExpressionWrapper,
)


@admin.register(FoodEntity)
class FoodEntityAdmin(admin.ModelAdmin):
    readonly_fields = ("image_thumbnail", "detailed_image_preview",)

    list_display = (
        "image_thumbnail",
        "name",
        "proteins",
        "fats",
        "carbs",
        "fibers",
        "calories",
        "creator",
    )
    
    fields = (
        "name",
        "detailed_image_preview",
        "image",
        "description",
        "proteins",
        "fats",
        "carbs",
        "fibers",
        "calories",
    )

    @admin.display(description="Фото")
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" '
                'style="object-fit: cover;" />',
                obj.image.url
            )

        return "-"

    @admin.display(description="Предпросмотр")
    def detailed_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 5px;" />',
                obj.image.url
            )

        return "Нет изображения"

    
    def save_model(self, request, obj, form, change):
        if not obj.creator_id:
            obj.creator = request.user

        
        super().save_model(request, obj, form, change)


@admin.register(FoodRecord)
class FoodRecordAdmin(admin.ModelAdmin):
    readonly_fields = ("image_thumbnail",)

    list_display = (
        "image_thumbnail",
        "created_at",
        "food_name",
        "grams",
        
        "food_proteins",
        "food_fats",
        "food_carbs",
        "food_fibers",
        "food_calories",
    )

    fields = (
        "food_base",
        "grams",
        "day_dairy"
    )

    # Изображение продукта
    @admin.display(description="Фото")
    def image_thumbnail(self, obj):
        if obj.food_base.image:
            return format_html(
                '<img src="{}" width="60" height="60" '
                'style="object-fit: cover;" />',
                obj.food_base.image.url
            )

        return "-"

    # Полезные элементы (белок, жир, углеводы, клетчатка, калории)
    @admin.display(description="Белок", ordering="food_base__proteins")
    def food_proteins(self, obj):
        return f"{obj.food_base.proteins*obj.grams/100:.1f}"

    @admin.display(description="Жир", ordering="food_base__fats")
    def food_fats(self, obj):
        return f"{obj.food_base.fats*obj.grams/100:.1f}"
    
    @admin.display(description="Углеводы", ordering="food_base__carbs")
    def food_carbs(self, obj):
        return f"{obj.food_base.carbs*obj.grams/100:.1f}"
    
    @admin.display(description="Клетчатка", ordering="food_base__fibers")
    def food_fibers(self, obj):
        return f"{obj.food_base.fibers*obj.grams/100:.1f}"
    
    @admin.display(description="Калории", ordering="food_base__calories")
    def food_calories(self, obj):
        return f"{obj.food_base.calories*obj.grams/100:.1f}"


    # Другие поля
    @admin.display(description="Продукт", ordering="food_base__name")
    def food_name(self, obj):
        return obj.food_base.name
    
    @admin.display(description="Дата", ordering="create_date")
    def created_at(self, obj):
        return obj.create_date.strftime("%d.%m.%Y %H:%M:%S")



@admin.register(DayDairy)
class DayDairyAdmin(admin.ModelAdmin):
    exclude = ("owner",)

    list_display = (
        "created_at",
        "title",
        "description_formatted",
        "total_proteins",
        "total_calories",
        "total_fibers",
    )


    @admin.display(description="Дата", ordering="create_date")
    def created_at(self, obj):
        return obj.create_date.strftime("%d.%m.%Y")

    @admin.display(description="Описание")
    def description_formatted(self, obj):
        return Truncator(obj.description).chars(40) if obj.description else "-"


    # Полезные элементы подсчет за день
    @admin.display(description="Белок/день")
    def total_proteins(self, obj):
        proteins_expression = Sum(
            ExpressionWrapper(
                F("food_base__proteins") * F("grams") / Value(Decimal("100")),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )

        total = obj.food_day_dairy.aggregate(
            proteins=proteins_expression
        )["proteins"] or 0

        return "{:.2f}".format(total)


    @admin.display(description="Калории/день")
    def total_calories(self, obj):
        calories_expression = Sum(
            ExpressionWrapper(
                F("food_base__calories") * F("grams") / Value(Decimal("100")),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )

        total = obj.food_day_dairy.aggregate(
            calories=calories_expression
        )["calories"] or 0

        return "{:.2f}".format(total)

    
    @admin.display(description="Клетчатка/день")
    def total_fibers(self, obj):
        fibers_expression = Sum(
            ExpressionWrapper(
                F("food_base__fibers") * F("grams") / Value(Decimal("100")),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )

        total = obj.food_day_dairy.aggregate(
            fibers=fibers_expression
        )["fibers"] or 0

        return "{:.2f}".format(total)


    def save_model(self, request, obj, form, change):
        if not obj.owner_id:
            obj.owner = request.user

        
        # Проверка существует ли запись за сегодня или нет
        today = timezone.localdate()

        dairy_existance = DayDairy.objects.filter(
            owner=request.user,
            create_date__date=today
        ).exists()

        if dairy_existance:
            raise ValidationError("Дневник за сегодня уже существует")


        super().save_model(request, obj, form, change)