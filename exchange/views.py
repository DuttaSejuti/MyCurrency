from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Currency
from .serializers import CurrencySerializer, ConvertSerializer
from .services import get_exchange_rate_data
import datetime

class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

class ConvertAPIView(APIView):
    def post(self, request):
        serializer = ConvertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        source_code = serializer.validated_data['source_currency']
        target_code = serializer.validated_data['exchanged_currency']
        amount = serializer.validated_data['amount']

        try:
            source = Currency.objects.get(code=source_code)
            target = Currency.objects.get(code=target_code)
        except Currency.DoesNotExist:
            return Response({"error": "Invalid currency code"}, status=status.HTTP_400_BAD_REQUEST)

        rate = get_exchange_rate_data(source_currency=source, exchanged_currency=target, valuation_date=datetime.date.today())
        converted_amount = amount * rate

        return Response({
            "rate": rate,
            "converted_amount": converted_amount
        })
