from django.contrib import admin
from mainapp.models import Comment, Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):  
    list_display = ('post_id', 'title', 'type', 'descendant', 'author', 'score', 'source', 'time', 'date_added')
    list_filter = ('type', 'descendant')
    search_fields = ('type', 'author', 'title')

# @admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_id', 'type', 'post', 'nested_comment', 'author', 'time', 'date_added')
    list_filter = ('type', 'author', 'time')
    search_fields = ('type',)

admin.site.register(Comment, CommentAdmin)