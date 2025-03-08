from django.urls import path
from . import views

urlpatterns = [
    # Other URL patterns
    path('check_boycott/', views.check_boycott, name='check_boycott'),
    path('get_alternatives/', views.get_alternatives, name='get_alternatives'),
]
