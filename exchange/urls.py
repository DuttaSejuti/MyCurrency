from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CurrencyViewSet, ConvertAPIView, RateListAPIView

router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet)

urlpatterns = router.urls + [
    path('convert/', ConvertAPIView.as_view(), name='convert'),
    path('rates/', RateListAPIView.as_view(), name='rates'),
]
