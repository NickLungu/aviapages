from django.contrib import admin
from django.urls import path
from aircrafts import views

urlpatterns = [
    path('', views.main_page_view, name='home'),
    path('search',views.searching, name='search'),
    path('aircraft_details/<str:tail_number>/', views.aircraft_info, name='details')
]
