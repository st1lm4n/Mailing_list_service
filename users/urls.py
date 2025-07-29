from django.urls import path

from users import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('activation_sent/', views.activation_sent, name='activation_sent'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]
