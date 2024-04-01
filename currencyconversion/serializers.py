from rest_framework import serializers
from .models import CurrencyConversion

# Create a serializer class for the CurrencyConversion model
# This class will be used to serialize CurrencyConversion objects into JSON format
class CurrencyConversionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyConversion
        fields = '__all__'