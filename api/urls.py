from django.urls import path
from api.views import HomeView

app_name = 'api'
urlpatterns = [
    path("register", HomeView.as_view()),
]