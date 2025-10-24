"""
URL Configuration for security demo
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('users/', views.get_users, name='users'),
    path('user/<int:user_id>/', views.get_user, name='user'),
    path('search/', views.search_users, name='search'),
    path('stats/', views.get_stats, name='stats'),
]
