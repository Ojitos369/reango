from django.urls import path

from .views import index

app_name = 'views'
urlpatterns = [
    path('', index, name='index'),
]
