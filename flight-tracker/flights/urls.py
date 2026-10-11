from django.urls import path
from . import views

app_name = 'flights'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/flights/search/', views.api_search_flights, name='api_search'),
    path('api/flights/track/', views.api_flight_track, name='api_track'),
]
