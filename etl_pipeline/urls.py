from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Создаем router для автоматической генерации URL
router = DefaultRouter()
router.register(r"sources", views.DataSourceViewSet)
router.register(r"products", views.ProductViewSet)
router.register(r"sales", views.SalesDataViewSet)
router.register(r"metrics", views.DailyMetricsViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("summary/", views.sales_summary, name="sales-summary"),
]
