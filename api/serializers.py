from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from mainapp.models import Post, Comment
import random

class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ['post_id','title','type','text','url','time','author','source', 'comment_count']
    

class PostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields="__all__"

    def validate(self, data):
        return data

    def update(self, instance, validated_data):
        if instance:
            Post.objects.filter(post_id=instance.pk).update(**validated_data)

        return instance


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['comment_id','type','text','post','date_updated','author', 'nested_comment_count']
    