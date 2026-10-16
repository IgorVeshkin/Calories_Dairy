from django.db import models

from django.contrib.auth.models import User

import uuid

class BaseModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    update_date = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        abstract = True


def image_save_path(instance, filename):
    return 'users/{0}/foods/{1}/{2}'.format(instance.creator.pk, instance.name, filename)

class FoodEntity(BaseModel):
    name = models.CharField(max_length=255, blank=False, null=False, verbose_name='Название')
    description = models.TextField(max_length=510, blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to=image_save_path, verbose_name='Изображение')

    proteins = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Белок')
    fats = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Жиры')
    carbs = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Углеводы')
    fibers = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Клетчатка')
    calories = models.DecimalField(max_digits=8, decimal_places=1, verbose_name='Калории')

    creator =  models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='food_entities',
        verbose_name='Создано'
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return '{} | Б-{:.0f}г, Ж-{:.0f}г, У-{:.0f}г, К-{:.0f}, Ккал-{:.0f}'.format(self.name, self.proteins, self.fats, self.carbs, self.fibers, self.calories) 


class FoodRecord(BaseModel):
    food_base = models.ForeignKey(
        FoodEntity, 
        on_delete=models.CASCADE,
        related_name='food_records',
        verbose_name='Продукт'
    )

    grams = models.DecimalField(max_digits=8, decimal_places=0, verbose_name='Грамм')

    day_dairy = models.ForeignKey(
        'DayDairy', 
        on_delete=models.CASCADE,
        related_name='food_day_dairy',
        verbose_name='Дневник'
    )

    class Meta:
        verbose_name = 'Запись продукта'
        verbose_name_plural = 'Записи продуктов'

    
    def __str__(self):
        return '{} | {} {:.0f} грамм: {:.1f} ккал'.format(self.create_date.strftime('%d.%m.%Y'), self.food_base.name, self.grams, self.food_base.calories*self.grams/100) 


class DayDairy(BaseModel):
    title = models.CharField(max_length=255, blank=False, null=False, verbose_name='Название')
    description = models.TextField(max_length=510, blank=True, verbose_name='Описание')

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='calories_dairies'
    )

    def __str__(self):
        return '{} | {}'.format(self.create_date.strftime('%d.%m.%Y'), self.title)

    class Meta:
        verbose_name = 'Дневник'
        verbose_name_plural = 'Дневники'
