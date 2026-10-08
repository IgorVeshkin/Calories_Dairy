from rest_framework import serializers

from .models import DayDairy

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
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = DayDairy
        fields = (
            'title', 
            'description', 
            'total_proteins', 
            'total_fats', 
            'total_carbs', 
            'total_fibers',
            'total_calories',
        )