from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("analytics/", views.analytics_view, name="analytics"),
    path(
        "api/sales-revenue-chart/",
        views.sales_revenue_chart_data,
        name="sales-revenue-chart",
    ),
    path(
        "api/top-products-chart/",
        views.top_products_chart_data,
        name="top-products-chart",
    ),
    path(
        "api/category-sales-data/",
        views.category_sales_data,
        name="category-sales-data",
    ),
]
