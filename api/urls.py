from django.urls import path
from api.views import PostListView, PostDetailView, CommentDetailView

app_name = 'api'
urlpatterns = [
    path("posts", PostListView.as_view()),
    path("posts/<int:id>", PostDetailView.as_view()),
    path("posts/<int:id>/comment", CommentDetailView.as_view()),
]