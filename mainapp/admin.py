from django.contrib import admin
from mainapp.models import Comment, Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):  
    list_display = ('post_id', 'title', 'type', 'descendant', 'author', 'score', 'source', 'time', 'date_added')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_id', 'type', 'post', 'author', 'time', 'date_added')

