from django.urls import path
from mainapp.views import HomeView

app_name = 'mainapp'
urlpatterns = [
    path("register", HomeView.as_view()),
]