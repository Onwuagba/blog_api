from django.urls import path
from mainapp.views import TopNewsView

app_name = 'mainapp'
urlpatterns = [
    path("topnews/", TopNewsView.as_view()),
]