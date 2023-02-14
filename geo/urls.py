from django.urls import path
from .views import GeoView

urlpatterns = [
    path('geo/',GeoView.as_view(), name='geo_list'),
    path('geo/<int:id>',GeoView.as_view(), name='geo_process'),
]