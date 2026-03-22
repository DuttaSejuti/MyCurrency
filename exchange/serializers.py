from rest_framework import serializers
from .models import Currency

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'

class ConvertSerializer(serializers.Serializer):
    source_currency = serializers.CharField(max_length=3, required=True)
    exchanged_currency = serializers.CharField(max_length=3, required=True)
    amount = serializers.DecimalField(max_digits=18, decimal_places=6, required=True)

class RateListSerializer(serializers.Serializer):
    source_currency = serializers.CharField(max_length=3, required=True)
    date_from = serializers.DateField(required=True)
    date_to = serializers.DateField(required=True)
