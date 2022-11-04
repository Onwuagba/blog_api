from django.urls import path
from mainapp.views import NewsView, NewsDetailView

app_name = 'mainapp'
urlpatterns = [
    path("news/", NewsView.as_view(), name='news_list'),
    path("news/<int:pk>", NewsDetailView.as_view(), name='news_detail'),
]